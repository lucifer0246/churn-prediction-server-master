from pydantic import BaseModel, Field
from typing import List


class PredictSingleValueResult(BaseModel):
  is_chrun : bool = Field(...)

class PredictMultipleValueResult(BaseModel):
  result: List[int] = Field(...)