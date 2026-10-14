# Aquí inicializamos la aplicación, registramos los routers y configuramos los middlewares básicos.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_auth
from app.api import routes_users
from app.api import routes_products
from app.api import routes_cart

from app.db.database import  engine
from app.db.database import Base
from app.models import user, product


# Crear la instancia principal de FastAPI
app = FastAPI (
    title= "E-commerce API",
    description= "Backend en FastAPI + PostgreSQL para aplicación de Flutter",
    version="1.0.0"
)

#-------------------- CONFIGURACIÓN CORS------------------
# Permite la petición desde el Front-end (Flutter u otros orígenes)
origins = [
    "https://localhost:3000",  # Ejemplo: web local
    "https://localhost:5173",  # Flutter web local
    "https://127.0.0.1:5173",
    "*",                       # Se puede dejarlo abierto en desarrollo
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,    # Dominios permitidos
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Registrar Routers
app.include_router(routes_auth.router)
app.include_router(routes_users.router)
app.include_router(routes_products.router)
app.include_router(routes_cart.router)

# --------------------- CREAR TABLAS AUTOMÁTICAMENTE (solo en desarrollo) ----------------------
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tablas creadas correctamente!!!")
    
@app.on_event("shutdown")
async def shutdown_event():
    await engine.dispose(   )

# --------------------- RUTA DE PRUEBA ----------------------
@app.get("/", tags = ["Root"])
async def read_root():
    return {"message": "Bienvenido a la API de E-commerce"}