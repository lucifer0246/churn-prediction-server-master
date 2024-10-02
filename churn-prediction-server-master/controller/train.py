from io import  BytesIO
from typing import BinaryIO
import pymongo
from pymongo.database import Database
from fastapi import UploadFile, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from models.train import DatasetModel, PreporcessingModel, BestModel
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import  ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFECV
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier
import pandas as pd 
import numpy as np
import os
from datetime import datetime
import pickle

from di import database
from schemas.response.train import GetAllModelsInformationResponse, ModelInformation

class TrainModel():

  def __init__(self,db:Database =Depends(database.get_db)) -> None:
    self.db = db

  async def get_all_models(self):
    collection = self.db.get_collection('bestmodel')
    doc_count = await collection.count_documents({})
    models = []
    try:
      cursor = collection.find({},{"model":False}).sort('accurancy',pymongo.DESCENDING)

      docs = await cursor.to_list(doc_count)

      for doc in docs:
        model = ModelInformation(**doc)
        models.append(model)

    except Exception as e:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail={
        'status':'failed',
        'message':'Something went wrong. Please try again later.'
      })
    finally:
      await cursor.close()
  
    return GetAllModelsInformationResponse(models=models);

  async def train_model(self):

    try:
      X_train, X_test, y_train, y_test = await self._data_preprocessing()
      await self._train_select_model(X_train, X_test, y_train, y_test)
    except Exception as e:
      print(e)
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail={
        'status':'failed',
        'message':'Failed to train model. Try again later'
      })


    return JSONResponse(status_code=status.HTTP_200_OK,content={
      'status':'success',
      'message':'Trained model successfully',
    })

  async def _train_select_model(self,X_train,X_test,y_train,y_test):

    models = [{
        'name':'Logistic Regression',
        'classifier' : LogisticRegression()
      },
      {
        'name':'K Neighbors Classifier',
        'classifier' : KNeighborsClassifier()
      },
      {
        'name':'Support Vector Machine',
        'classifier':SVC(kernel='rbf',random_state=42),
      },
      {
        'name':'Random Forest Classifier',
        'classifier':RandomForestClassifier(n_estimators=20, criterion="entropy", random_state=42)
      },
      {
        'name':'Naive Bayes Classifiers',
        'classifier':GaussianNB(),
      }
    ]

    trained_models = [] 

    for model in models:
      classifier = model['classifier']
      classifier.fit(X_train,y_train)
      y_pred = classifier.predict(X_test)
      accurancy = accuracy_score(y_test, y_pred)
      precision = precision_score(y_test,y_pred)
      recall = recall_score(y_test,y_pred)
      f_score = f1_score(y_test,y_pred)
      model_obj = BestModel(model=pickle.dumps(classifier),accurancy=accurancy,model_name=model['name'],precision=precision,recall=recall,f_score=f_score)
      trained_models.append(model_obj.model_dump())

    collection = self.db.get_collection('bestmodel')
    await collection.delete_many({})
    await collection.insert_many(trained_models)


  async def _data_preprocessing(self):
    
    dataset_info = DatasetModel(**await self.db.get_collection('dataset').find_one({}))
    df = pd.read_csv(f'dataset/{dataset_info.file_name}')
    
    df['TotalCharges'].replace(" ",np.nan,inplace=True)
    df.dropna(subset=['TotalCharges'], inplace=True)

    # convert the numberic string to number (TotalCharges)
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'])

    # converting the SeniorCitizen from numbric to categorical in for to preprocess
    df['SeniorCitizen'] = df['SeniorCitizen'].map({0:'Yes',1:'No'})

    X = df.iloc[:,1:-1]
    y = df.iloc[:,-1]

    # encoding binary feature
    X['gender'] = X['gender'].map({'Male':0,'Female':1})

    y = y.map({'No':0,'Yes':1})

    for col in ['SeniorCitizen','Partner','Dependents','PhoneService','PaperlessBilling']:
      X[col] = X[col].map({'No':0,'Yes':1})

    y = y.values

    one_hot_encode_idx = []

    for idx, col in enumerate(X.columns):
        unique_count = len(df[col].unique())
        
        if unique_count == 3 or unique_count == 4:
            one_hot_encode_idx.append(idx)

    X = X.values

    # encoding the categorical data
    ct = ColumnTransformer(transformers=[('one_hot_encoder',OneHotEncoder(),one_hot_encode_idx)], remainder='passthrough')
    X = np.array(ct.fit_transform(X))

    # Scaling the features

    sc = StandardScaler()

    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.30,random_state=50)
    
    X_train = sc.fit_transform(X_train,y_train)
    X_test = sc.transform(X_test)

    estimator = LogisticRegression()
    rfecv = RFECV(estimator, cv=StratifiedKFold(10, random_state=50, shuffle=True), scoring="accuracy")
    rfecv.fit(X_train, y_train)

    X_train_rfe = rfecv.transform(X_train)
    X_test_rfe = rfecv.transform(X_test)

    ct_serialized = pickle.dumps(ct)
    sc_serialized = pickle.dumps(sc)
    rfecv_serialized = pickle.dumps(rfecv)
    doc = PreporcessingModel(standart_scalar=sc_serialized,column_transformer=ct_serialized,rfecv=rfecv_serialized)
    
    collection = self.db.get_collection('preprocessing')
    await collection.delete_many({})
    model_info_dict = doc.model_dump()
    model_info_dict.pop('id')
    await collection.insert_one(model_info_dict)
    return X_train_rfe, X_test_rfe, y_train, y_test
    

  async def upload_csv_file(self,dataset:UploadFile):
    if(dataset.content_type != 'text/csv'):
      return JSONResponse(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,content={
        'status':'fail',
        'message':'Dataset should be CSV file!'
      })
    
    df = pd.read_csv(dataset.file) 
    if(len(df.columns) != 21):
      raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail={
        'status':'failed',
        'message':'Please upload CSV which contains valid data.'
      })
    
    dataset.file.seek(0)  
    dir = 'dataset'
    os.makedirs(dir,exist_ok=True)
    
    
    for old_file in os.listdir(dir):
      os.unlink(f'{dir}/{old_file}')


    file_name = dataset.filename
    with open(f'{dir}/{file_name}', "wb") as buffer:
        buffer.write(dataset.file.read())

    dataset_collection = self.db.get_collection('dataset')

    doc_count: int = await dataset_collection.count_documents({})
    if doc_count > 0:
      await dataset_collection.delete_many({})

    await dataset_collection.insert_one({
      'file_name':file_name,
      'upload_date_time':datetime.utcnow()
    })

    return JSONResponse(status_code=status.HTTP_200_OK,content={
      'status':'success',
      'message':'File uploaded successfully!'
    })
    