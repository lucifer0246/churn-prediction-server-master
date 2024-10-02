from pydantic import BaseModel,EmailStr, Field, field_validator
import re

class CreateUser(BaseModel):

  email:EmailStr
  password:str = Field(...)
  confirm_password:str = Field(...)

  @field_validator('password')
  @classmethod
  def password_validator(cls,value:str):
    if not re.search(r'\d', value):
        raise ValueError('password must contain at least one digit')
        
    
    # Check if the password contains at least one uppercase letter
    if not re.search(r'[A-Z]', value):
        raise ValueError('password must contain at least one capital letter')
    
    # Check if the password contains at least one lowercase letter
    if not re.search(r'[a-z]', value):
        raise ValueError('password must contain at least one small letter')
    
    # Check if the password contains at least one special character
    if not re.search(r'[@#$%^&+=!?*]', value):
        raise ValueError('password must contain at least one special character')
    
    # Check if the length of the password is at least 8 characters
    if len(value) < 8:
        raise ValueError('password must contain at least 8 characters')
    
    # If all conditions pass, return True
    return value

class Login(BaseModel):
  email: EmailStr
  password: str