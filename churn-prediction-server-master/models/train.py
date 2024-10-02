from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime
from typing import Optional, Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class DatasetModel(BaseModel):
  """
   Model for dataset information.
  """
  id: Optional[PyObjectId]= Field(alias='_id', default=None)
  file_name: str = Field(...)
  upload_date_time: datetime = Field(...)

class BestModel(BaseModel):
  """
    Model for storing the best model.
  """
  id: Optional[PyObjectId]= Field(default_factory=PyObjectId,alias='_id',serialization_alias='_id')
  accurancy: float = Field(...)
  precision: float = Field(...)
  recall:float = Field(...)
  f_score:float = Field(...)
  model: bytes = Field(...)
  model_name: str = Field(...)

class PreporcessingModel(BaseModel):
  """
    Model for preprocessing objects, such as StandartScalar, ColumnTranformer, rfecv.
  """
  id: Optional[PyObjectId]= Field(alias='_id', default=None)
  standart_scalar: bytes = Field(...)
  column_transformer: bytes = Field(...)
  rfecv: bytes = Field(...)