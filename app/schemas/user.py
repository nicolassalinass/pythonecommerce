#Esquemas de VALIDACIÓN o ESTRUCTURACIÓN de los datos que llegan o salen de la API.(Pydantic)
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# Campos comunes compartidos entre esquemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    rol: Optional [str] = "customer"
    is_active: Optional[bool] = True
    
# Esquema para CREACIÓN de usuario (Registro)
class UserCreate(UserBase):
    password: str = Field(..., min_length = 6, max_length = 100)
    
class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Permite convertir desde SQLAlchemy
    
# Esquema para ACTUALIZAR datos del usuario (campos opcionales)
class UserUpdate(BaseModel):
    name: Optional [str] = Field(None, min_length = 2, max_length = 100)
    password: Optional [str] = Field(None, min_length = 6, max_length = 100)
    rol: Optional [str] = None
    is_active: Optional[bool] = None
    
# Esquema de SALIDA (lo que devuelve al front-end)
class UserOut(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True 
        
# Esquema INTERNO (para el uso del back-end)
class UserInDB(UserBase):
    id: int
    hashed_password: str
    created_at: datetime
    
    class Config:
        orm_mode: True