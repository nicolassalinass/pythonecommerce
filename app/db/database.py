# Este archivo creará el motor asíncrono de SQLAlchemy y la sesión para interactuar con la base de datos.
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# URL de conexión (ejemplo: PostgreSQL)
DATABASE_URL ="postgresql+asyncpg://postgres:admin@localhost:5432/db_ecommerce"

# Línea de código para crear el motor asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Línea de código para crear la sesión asíncrona
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para modelos
Base = declarative_base()

# Dependencia para inyectar sesión en rutas
async def get_db():
    async with async_session() as session:
        yield session