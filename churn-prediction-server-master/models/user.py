from typing import Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]

class User(BaseModel):
  id:Optional[PyObjectId] = Field(alias='_id', default=None)
  email:str = Field(...)
  role:str = Field(...)
  password:str = Field(...)
