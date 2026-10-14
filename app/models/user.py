# Modelo de USUARIO (SQLALchemy)
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "usuarios" #nombre de la tabla en PostreSQL
    
    id = Column(Integer, primary_key = True, index = True)  # Clave primaria autoincremental
    
    name = Column(String(70), nullable = False)  # Nombre del usuario
    
    email = Column(String(70), unique = True, index = True, nullable = False) # Correo electrónico único del usuario
    
    hashed_password = Column(String, nullable = False)
    # El formato hash se refiere a la cadena alfanumérica de longitud fija
    # que resulta de aplicar un algoritmo matemático (función hash) a un conjunto de datos,
    # sirviendo como una huella digital única e irrepetible para ese dato, usada para verificar integridad, autenticar y almacenar contraseñas.
    #  Un hash es unidireccional, lo que significa que es casi imposible revertir el hash para obtener los datos originales.
    
    rol = Column(String(50), default ="customer")  # Rol del usuario (por ejemplo: "customer"(cliente) o "admin" (administrador xddd))
    
    is_active = Column(Boolean, default = True)  # Verifica el estado de la cuenta (activo / inactivo)
    
    created_at = Column(DateTime(timezone = True), server_default= func.now()) # Fecha y hora de creación del registro (utilizamos para esto timestamp del servidor)
    
    