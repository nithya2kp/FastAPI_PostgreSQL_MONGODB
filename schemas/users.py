from pydantic import BaseModel,EmailStr, Field
from pydantic.generics import  GenericModel
from typing import TypeVar,Generic,Optional

T = TypeVar('T')   # type variable for generic typing


# Pydantic model for UserCreate
class UserCreate(BaseModel):
    full_name: str
    email : EmailStr
    password : str = Field(..., min_length=4)
    phone: str

# Pydantic model for UserUpdate
class UserUpdate(BaseModel):
    full_name: str = None
    email: str = None
    password: str = None
    phone: str = None
    user_id: int = None

# Pydantic model  request with parameter for UserUpdate
class RequestNew(BaseModel):
    parameter: UserUpdate = Field(...)


# Generic Pydantic model for a response

class Response(GenericModel,Generic[T]):
    code: str
    status: str
    message: str
    result: Optional[T]