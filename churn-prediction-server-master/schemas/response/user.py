from pydantic import BaseModel, BeforeValidator, Field
from typing import Optional, Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class ErrorResponse(BaseModel):
  message:str

class CreateUserResponse(BaseModel):
  id:Optional[PyObjectId] = Field(alias='_id', default=None,serialization_alias='id')
  email:str
  role:str
  access_token:str


class GetCurrentUserResponse(BaseModel):
  id:Optional[PyObjectId] = Field(alias='_id', default=None,serialization_alias='id')
  email:str
  role:str

