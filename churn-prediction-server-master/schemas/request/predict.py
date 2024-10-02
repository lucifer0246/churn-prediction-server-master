from pydantic import BaseModel, Field
from enum import Enum

from typing import Optional

class Gender(str, Enum):
  Male = 'Male'
  Female = 'Female'

class Binary(str,Enum):
  Yes = 'Yes'
  No= 'No'

class MultipleLine(str,Enum):
  NoPhoneService = 'No phone service'
  Yes = 'Yes'
  No  = 'No'

class Service(str,Enum):
  NoInternetService = 'No internet service'
  Yes = 'Yes'
  No  = 'No'

class InternetService(str, Enum):
  DSL = 'DSL'
  FiberOptic = 'Fiber Optic'
  No = 'No'


class Contract(str, Enum):
  OneYear = 'One year'
  MonthToMont = 'Month-to-month'
  TowYear = 'Two year'

class PaymentMethod(str, Enum):
  ElectronicCheck = 'Electronic check'
  MailedCheck = 'Mailed check'
  CreditCard = 'Credit card (automatic)'
  BankTransfer = 'Bank transfer (automatic)'


class PredictSingleValue(BaseModel):
  """
    Schema for prediction of single value
  """
  customer_id: Optional[str] = Field(serialization_alias='customerID',default='NoId')
  gender: Gender = Field(..., serialization_alias='gender')
  senior_citizen: Binary = Field(..., serialization_alias='SeniorCitizen')
  partner: Binary = Field(..., serialization_alias='Partner')
  dependents: Binary = Field(..., serialization_alias='Dependents')
  tenure: int = Field(...,serialization_alias='tenure',ge=0)
  phone_service: Binary = Field(..., serialization_alias='PhoneService')
  multiple_lines: MultipleLine = Field(..., serialization_alias='MultipleLines')
  internet_service : InternetService = Field(..., serialization_alias='InternetService')
  online_security : Service = Field(..., serialization_alias='OnlineSecurity')
  online_backup : Service = Field(..., serialization_alias='OnlineBackup')
  device_protection: Service = Field(..., serialization_alias='DeviceProtection')
  tech_support: Service = Field(..., serialization_alias='TechSupport')
  streaming_tv : Service = Field(..., serialization_alias='StreamingTV')
  streaming_movies: Service = Field(..., serialization_alias='StreamingMovies')
  contract: Contract = Field(..., serialization_alias='Contract')
  paperless_billing: Binary = Field(...,serialization_alias='PaperlessBilling')
  payment_method: PaymentMethod = Field(..., serialization_alias='PaymentMethod')
  monthly_charges: float = Field(..., serialization_alias='MonthlyCharges',ge=0)
  total_charges: float = Field(..., serialization_alias='TotalCharges',ge=0)