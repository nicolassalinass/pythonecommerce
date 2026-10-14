from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ============================
#      BASE
# ============================

class UserBase(BaseModel):
    name: str
    email: EmailStr


# ============================
#      CREATE (ADMIN)
# ============================

class UserCreate(UserBase):
    password: str
    rol: Optional[str] = "customer"
    is_active: Optional[bool] = True


# ============================
#      RESPONSE
# ============================

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    rol: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        

# ============================
#      UPDATE ALL (ADMIN)
# ============================

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    rol: Optional[str] = None
    is_active: Optional[bool] = None

# ============================
#      UPDATE PERSONAL (USER)
# ============================

class UserUpdateSelf(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    
# ============================
#      CHANGE PASSWORD
# ============================

class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str