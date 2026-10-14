# Importamos FastAPI y utilidades para dependencias y errores
from fastapi import APIRouter, Depends, HTTPException

# Importamos la sesión asíncrona de SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession

# Dependencia para obtener la conexión a la base de datos
from app.db.database import get_db

# Importamos los esquemas de entrada/salida del carrito
from app.schemas.cart_schema import *

# Importamos las funciones CRUD del carrito
# IMPORTANTE: aquí importamos funciones individuales, no una clase
from app.crud.cart_crud import (
    get_cart,
    add_item,
    clear_cart,
)
from app.crud.cart_crud import remove_cart_item

# Dependencia para obtener al usuario autenticado actual
from app.core.auth import get_current_user


# Definimos el router para todos los endpoints de carrito
router = APIRouter(prefix="/cart", tags=["Cart"])


# ============================================================
# GET /cart
# Obtener el carrito del usuario o crearlo si no existe
# ============================================================
@router.get("/", response_model=CartOut)
async def get_user_cart(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Retorna el carrito del usuario.
    Si el carrito no existe todavía, se crea automáticamente.
    """

    # Se obtiene el carrito según el ID del usuario
    cart = await get_cart(db, current_user.id)

    # Si no existe, lo creamos
    if not cart:
        from app.crud.cart_crud import create_cart  # import aquí para evitar conflicto de nombres
        cart = await create_cart(db, current_user.id)

    return cart


# ============================================================
# POST /cart/add
# Agregar un producto al carrito
# ============================================================
@router.post("/add", response_model=CartItemOut)
async def add_cart_item(
    item: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Agrega un nuevo ítem al carrito del usuario.
    Si el ítem ya existe, aumenta la cantidad.
    """

    # Llamamos al CRUD que maneja agregar o sumar cantidades
    result = await add_item(
        db,
        current_user.id,
        item.product_id,
        item.quantity
    )

    # Si el CRUD retorna None, significa que el producto no existe
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")

    return result


# ============================================================
# DELETE /cart/item/{item_id}
# Eliminar un producto específico del carrito
# ============================================================
@router.delete("/item/{item_id}")
async def delete_cart_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Elimina un ítem específico del carrito del usuario.
    """

    success = await remove_cart_item(db, current_user.id,item_id)

    if not success:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Item removed"}



# @router.put("/item/{item_id}/quantity", response_model=CartItemOut)
# async def update_item_quantity(
#     item_id: int,
#     new_quantity: int,
#     db: AsyncSession = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     """
#     Actualiza la cantidad exacta de un ítem del carrito.
#     Si new_quantity = 0 → Elimina el item.
#     """

#     from app.crud.cart_crud import update_quantity

#     updated_item = await update_quantity(db, item_id, new_quantity)

#     if updated_item is None:
#         raise HTTPException(status_code=404, detail="Item not found")

#     return updated_item


@router.put("/item/{item_id}/quantity", response_model=CartItemOut)
async def update_item_quantity(
    item_id: int,
    new_quantity: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    from app.crud.cart_crud import update_quantity

    updated_item = await update_quantity(
        db=db,
        user_id=current_user.id,
        item_id=item_id,
        new_quantity=new_quantity
    )

    if updated_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return updated_item


# ============================================================
# DELETE /cart/clear
# Vaciar todo el carrito del usuario
# ============================================================
@router.delete("/clear")
async def clear_user_cart(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Elimina todos los ítems del carrito del usuario.
    """

    await clear_cart(db, current_user.id)
    return {"message": "Cart cleared"}