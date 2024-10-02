from pydantic import BaseModel
from pydantic import BaseModel, BeforeValidator, Field
from typing import Optional, Annotated, List

PyObjectId = Annotated[str, BeforeValidator(str)]

class ModelInformation(BaseModel):
  id: Optional[PyObjectId]= Field(alias='_id', default=None,serialization_alias='id')
  accurancy: float = Field(...)
  model_name: str = Field(...)
  precision: float = Field(...)
  recall:float = Field(...)
  f_score:float = Field(...)

class GetAllModelsInformationResponse(BaseModel):
  models: List[ModelInformation] = Field(...)