# Creamos funciones asíncronas que utilicen la sesión de base de datos (AsyncSession) para interactuar con PostgreSQL.
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.db.database import Base
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate
from typing import Optional, List


class UserCRUD:
    
    # Creamos el usuario
    async def create_user(self, db: AsyncSession, user: UserCreate, hashed_password: str) -> User:
        new_user = User(
            name = user.name,
            email = user.email,
            hashed_password = hashed_password,
            rol = user.rol,
            is_active=user.is_active
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    # Obtener Usuario por ID
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    # Obtener usuario por correo
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    # Obtener todos los usuarios
    async def get_all_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    # Actualizar usuario
    async def update_user(self, db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
        existing_user = await get_user_by_id(db, user_id)
        if not existing_user:
            return None

        for field, value in user_update.model_dump(exclude_unset=True).items():
            setattr(existing_user, field, value)

        db.add(existing_user)
        await db.commit()
        await db.refresh(existing_user)
        return existing_user

    # Eliminar usuario
    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        existing_user = await get_user_by_id(db, user_id)
        if not existing_user:
            return False

        await db.delete(existing_user)
        await db.commit()
        return True

# Instancia obligatoria para que FastAPI pueda importarlo
user_crud = UserCRUD()