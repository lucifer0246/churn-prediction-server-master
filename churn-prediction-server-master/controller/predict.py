from bson.objectid import ObjectId
from pymongo.database import Database
from fastapi import Depends, HTTPException, status, UploadFile
from di import database
import pandas as pd
from pandas import DataFrame
from schemas.request.predict import PredictSingleValue
from models.train import PreporcessingModel, BestModel
import numpy as np
from numpy import ndarray
import pickle
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import RFECV

from schemas.response.Predict import PredictMultipleValueResult, PredictSingleValueResult


class PredictController():

  def __init__(self,db:Database =Depends(database.get_db)) -> None:
    self.db = db

  async def predict_single_value(self,value:PredictSingleValue, selected_model_id:str):
    json_data = value.model_dump(by_alias=True,mode='json')
    df = pd.json_normalize(json_data)
    try:
      dataset = await self._data_preprocessing(df)
      result  = await self._predict(dataset, selected_model_id)
      
    except Exception as e:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail={
        'status':'fail',
        'message':'Failed to predict value.'
      })
    
    is_churn = False

    if result[0] == 0 :
      is_churn = False
    else:
      is_churn = True
    
    return PredictSingleValueResult(is_chrun=is_churn)

  async def predict_multiple_value(self,file:UploadFile,selected_model_id:str):

    if(file.content_type != 'text/csv'):
      raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,detail={
        'status':'fail',
        'message':'Dataset should be CSV file!'
      })
    
    try:
      df = pd.read_csv(file.file)

      if(len(df.columns) != 20):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail={
          'status':'failed',
          'message':'Please upload CSV which contains valid data.'
        })
      
      dataset = await self._data_preprocessing(df)
      result = await self._predict(dataset, selected_model_id)
    except HTTPException as e:
      raise e

    except Exception as e:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail={
        'status': 'failed',
        'message':'Failed to predict!. Please try after sometime'
      })

    return PredictMultipleValueResult(result=result)
          

  async def _data_preprocessing(self,df:DataFrame):

    # convert the numberic string to number (TotalCharges)
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'])

    X = df.iloc[:,1:]

    # converting the SeniorCitizen from numbric to categorical in for to preprocess
    if(X['SeniorCitizen'].unique().__contains__([0,1])):
      X['SeniorCitizen'] = X['SeniorCitizen'].map({0:'No',1:'Yes'})
  

    # encoding binary feature
    X['gender'] = X['gender'].map({'Male':0,'Female':1})
    

    for col in ['SeniorCitizen','Partner','Dependents','PhoneService','PaperlessBilling']:
      X[col] = X[col].map({'No':0,'Yes':1})

    X = X.values
    collection = self.db.get_collection('preprocessing')
    doc = await collection.find_one({})
    
    preprocessing_obj = PreporcessingModel(**doc)
    ct: ColumnTransformer = pickle.loads(preprocessing_obj.column_transformer)
    sc: StandardScaler = pickle.loads(preprocessing_obj.standart_scalar)
    rfecv:RFECV =  pickle.loads(preprocessing_obj.rfecv)

    X = np.array(ct.transform(X))
    X = sc.transform(X)
    X = rfecv.transform(X)
    return X
  
  async def _predict(self,dataset:ndarray,selected_model_id:str) -> ndarray:
    collection = self.db.get_collection('bestmodel')
    doc = await collection.find_one(ObjectId(selected_model_id))
    selectedModel = BestModel(**doc)
    classifier = pickle.loads(selectedModel.model)

    return classifier.predict(dataset)