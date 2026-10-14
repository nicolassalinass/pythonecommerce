# Creando las Rutas Básicas para la API
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from app.db.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate, ChangePasswordSchema, UserUpdateSelf
from app.core.auth import require_role, get_current_active_user,  get_current_user
from app.core.security import verify_password

router = APIRouter(prefix="/users", tags=["Users"])
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# ============================================
#   CREAR un Usuario (solo ADMIN)
# ============================================


@router.post("/", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))]
)
async def create_user(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    try:
        hashed_password = pwd_context.hash(user.password)

        new_user = User(
            name=user.name,
            email=user.email,
            hashed_password=hashed_password,
            rol=user.rol,
            is_active=user.is_active
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="El email ya está registrado.")


# ============================================
#  OBTENER todos los Usuarios  (solo ADMIN)
# ============================================


@router.get("/", 
    response_model=list[UserResponse],
    dependencies=[Depends(require_role("admin"))]
)
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()


# ============================================
#   OBTENER Usuario por ID (solo ADMIN)
# ============================================


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_role("admin"))]
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado!")
    return user


# ============================================
#   ACTUALIZAR Usuario  (solo ADMIN)
# ============================================


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_role("admin"))]
)
async def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado!")

    if user_update.name:
        user.name = user_update.name

    if user_update.rol:
        user.rol = user_update.rol

    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    if user_update.password:
        user.hashed_password = pwd_context.hash(user_update.password)

    await db.commit()
    await db.refresh(user)
    return user


# ============================================
#   ELIMINAR Usuario (solo ADMIN)
# ============================================


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))]
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado!")

    await db.delete(user)
    await db.commit()

    return {"message": f"Usuario {user_id} eliminado correctamente!"}

# ============================================
#   ACTUALIZAR perfil propio (solo usuario logueado)
# ============================================


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_update: UserUpdateSelf,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):

    if user_update.name is not None:
        current_user.name = user_update.name

    if user_update.email is not None:
        current_user.email = user_update.email

    await db.commit()
    await db.refresh(current_user)

    return current_user

# ============================================
#   CAMBIAR  contraseña
# ============================================


@router.put("/me/change-password")
async def change_my_password(
    data: ChangePasswordSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):

    # Verificar contraseña actual
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta.")

    # Asignar nueva contraseña
    current_user.hashed_password = pwd_context.hash(data.new_password)

    await db.commit()
    await db.refresh(current_user)

    return {"message": "Contraseña actualizada correctamente."}