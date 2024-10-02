from fastapi import APIRouter, UploadFile, Depends
from controller import auth
from schemas.request.predict import PredictSingleValue
from controller.predict import PredictController
from controller.auth import get_current_user

from schemas.response.Predict import PredictMultipleValueResult, PredictSingleValueResult
from schemas.response.user import GetCurrentUserResponse

router = APIRouter(prefix='/predict',tags=['Predict'])


@router.post('/single-dataset', response_model=PredictSingleValueResult)
async def predict_single_value(single_value:PredictSingleValue,selected_model_id:str,predict_controller:PredictController = Depends(PredictController),current_user:GetCurrentUserResponse=Depends(auth.get_current_user)):
  response = await predict_controller.predict_single_value(single_value,selected_model_id)
  return response


@router.post('/upload-file', response_model=PredictMultipleValueResult)
async def predict_multiple_value(dataset:UploadFile,selected_model_id:str,predict_controller:PredictController = Depends(PredictController),current_user:GetCurrentUserResponse=Depends(auth.get_current_user)):
  response = await predict_controller.predict_multiple_value(dataset,selected_model_id)
  return response