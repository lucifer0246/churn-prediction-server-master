from datetime import datetime, timedelta
from bson import ObjectId
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from di import database
from pymongo.database import Database
from pymongo.results import InsertOneResult
from schemas.request.user import CreateUser, Login
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from models.user import User
from passlib.context import CryptContext
from config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas.response.user import CreateUserResponse, GetCurrentUserResponse

ALGORITHM='HS256'


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

async def get_current_user(token: str = Depends(oauth2_scheme),db:Database = Depends(database.get_db)) -> GetCurrentUserResponse:
  
  credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
          'status':'failed',
          'message':'Invalid access token! Please login again'
        },
        headers={"WWW-Authenticate": "Bearer"},
    )

  try:
    payload = jwt.decode(token=token,key=SECRET_KEY,algorithms=[ALGORITHM])
    expire_time = payload.get('expire_time')
    user_id = payload.get('user_id')

    if expire_time == None or user_id == None:
      raise credentials_exception
      
    expire_time_obj = datetime.strptime(expire_time,'%Y-%m-%d %H:%M:%S.%f')
      
    if expire_time_obj < datetime.utcnow():
      raise credentials_exception
      
    collection = db.get_collection('users')
    user = await collection.find_one({'_id':ObjectId(user_id)})
    if not user:
      raise credentials_exception

  except JWTError:
    raise credentials_exception
    
  except HTTPException as http_exception:
    raise http_exception;
    
  except Exception as e:
    print(e)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail={
      'status':'failed',
      'message':'Something went wrong! Please try after sometime.'
    })
    
  return GetCurrentUserResponse(**user)


class AuthContoller():
    
  def __init__(self,db:Database =Depends(database.get_db)) -> None:
    self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
    self.db = db


  def __verify_password(self,plain_pwd:str, hashed_pwd:str):
    return self.pwd_context.verify(plain_pwd, hashed_pwd)


  def __hashed_pwd(self,plain_pwd:str):
    return self.pwd_context.hash(plain_pwd)


  def __create_access_token(self,id:str):
    encode_to = {'user_id':id}
    expire_time = datetime.utcnow() + timedelta(hours=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    encode_to.update({'expire_time':str(expire_time)})
    encoded_jwt = jwt.encode(claims=encode_to,key=SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt


  async def login_user(self,data:Login):
    collection = self.db.get_collection('users')
    doc = await collection.find_one({'email':data.email})
    
    if doc == None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail={
        'status':'failed',
        'message':'No user found with this email address'
      })

    user = User(**doc)
    is_valid_password = self.__verify_password(data.password,user.password)
    if not is_valid_password:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail={
        'status': 'failed',
        'message':'Invalid password or email address!'
      })

    access_token = self.__create_access_token(str(doc['_id']))

    return CreateUserResponse(**doc,access_token=access_token)


  async def create_new_user(self,data:CreateUser):
    if data.password != data.confirm_password:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail={
        'status':'fail',
        'message':'Confirmed password is not same as password! Please confirm again.'
      })
    
    collection = self.db.get_collection('users')
    user = User(email=data.email,role='user',password=self.__hashed_pwd(data.password))

    doc_count = await collection.count_documents({'email':user.email})

    if doc_count >= 1:
      raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,detail={
        'status':'failed',
        'message':'Email already exist',
      })

    doc:InsertOneResult  = await collection.insert_one(user.model_dump())
    access_token = self.__create_access_token(str(doc.inserted_id))
    inserted_doc =await collection.find_one({'_id':doc.inserted_id})
    
    return JSONResponse(status_code=status.HTTP_201_CREATED,content=CreateUserResponse(**inserted_doc,access_token=access_token).model_dump_json(),headers={"WWW-Authenticate": f"Bearer {access_token}"}, )