# MODELOS DE LA BASE DE DATOS (SQLAlchemy)
# Representan las tablas "carrito" y "carrito_items"

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Cart(Base):
    """
    Tabla principal del carrito.
    Un carrito pertenece a un usuario (user_id).
    Contiene múltiples CartItem como relación uno-a-muchos.
    """
    __tablename__ = "carrito"

    id = Column(Integer, primary_key=True, index=True)

    # ForeignKey apunta a la tabla usuarios.id
    user_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True)

    # Relación con los items del carrito
    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
        lazy="selectin"  # recomendado para async
    )


class CartItem(Base):
    """
    Tabla de ítems dentro del carrito.
    Cada registro enlaza un carrito con un producto.
    """
    __tablename__ = "carrito_items"

    id = Column(Integer, primary_key=True, index=True)

    # Relación con el carrito
    cart_id = Column(Integer, ForeignKey("carrito.id"))

    # Relación con el producto
    product_id = Column(Integer, ForeignKey("productos.id"))

    quantity = Column(Integer, default=1)

    # Relaciones ORM
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", lazy="selectin")