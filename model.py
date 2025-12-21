from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float

class UserCreate(BaseModel):
    email : str
    password : str

class UserResponse(BaseModel):
    id: int 
    email: str 
    role: str 

    class confiq:
        from_attributes = True
