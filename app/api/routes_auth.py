# Rutas de autenticación: Estas rutas son los puntos de entrada desde la app Flutter hacia el backend FastAPI.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from app.db.database import get_db
from app import crud
from app.schemas.user_schema import UserCreate, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token, verify_access_token
from app.core.auth import get_current_active_user
from datetime import timedelta
from app.core.config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])

auth_scheme = HTTPBearer()

# ------------------------- REGISTRO ---------------------------
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):

    existing_user = await crud.user_crud.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed_password = get_password_hash(user_in.password)

    new_user = await crud.user_crud.create_user(db, user_in, hashed_password)
    return new_user

# ------------------------- LOGIN ----------------------------
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):

    user = await crud.user_crud.get_user_by_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales Inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

# ------ función get_current_user comentada porque ahora usamos -----------
# ------ la que se encuentra alojada en  app/core/auth.py. ----------------
"""async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: str = payload.get("sub")
    user = await crud.user_crud.get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user
    
"""

@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user = Depends(get_current_active_user)):
    return current_user