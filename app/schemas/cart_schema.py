# ESQUEMAS Pydantic del carrito
# Representan la entrada y salida según la API

from pydantic import BaseModel
from typing import List
from app.schemas.product_schema import ProductResponse


class CartItemOut(BaseModel):
    """
    Esquema de salida para un ítem del carrito.
    Incluye el producto serializado + cantidad.
    """
    id: int
    product: ProductResponse
    quantity: int

    class Config:
        from_attributes = True


class CartOut(BaseModel):
    """
    Carrito completo con la lista de ítems.
    """
    id: int
    items: List[CartItemOut]

    class Config:
        from_attributes = True


class CartItemCreate(BaseModel):
    """
    Datos necesarios para agregar un ítem al carrito.
    """
    product_id: int
    quantity: int = 1