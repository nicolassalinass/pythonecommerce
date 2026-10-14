# # CRUD del carrito - Acceso directo a la base de datos

# from sqlalchemy import select, delete
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.models.cart import Cart, CartItem
# from app.models.product import Product


# async def get_cart(db: AsyncSession, user_id: int):
#     """
#     Obtiene el carrito según el ID del usuario.
#     """
#     result = await db.execute(
#         select(Cart).where(Cart.user_id == user_id)
#     )
#     return result.scalar_one_or_none()


# async def create_cart(db: AsyncSession, user_id: int):
#     """
#     Crea un nuevo carrito para el usuario.
#     """
#     cart = Cart(user_id=user_id)
#     db.add(cart)
#     await db.commit()
#     await db.refresh(cart)
#     return cart


# async def add_item(db: AsyncSession, user_id: int, product_id: int, quantity: int):
#     """
#     Agrega un producto al carrito:
#     - Si el carrito no existe ➝ se crea
#     - Si el producto ya existe en el carrito ➝ suma cantidad
#     - Si el producto no existe ➝ lo agrega
#     """

#     # 1) Obtener carrito o crearlo
#     cart = await get_cart(db, user_id)
#     if not cart:
#         cart = await create_cart(db, user_id)

#     # 2) Verificar que el producto exista
#     product = await db.execute(select(Product).where(Product.id == product_id))
#     if not product.scalar_one_or_none():
#         return None

#     # 3) Verificar si ya existe el item
#     result = await db.execute(
#         select(CartItem).where(
#             CartItem.cart_id == cart.id,
#             CartItem.product_id == product_id
#         )
#     )
#     item = result.scalar_one_or_none()

#     if item:
#         item.quantity += quantity
#     else:
#         item = CartItem(
#             cart_id=cart.id,
#             product_id=product_id,
#             quantity=quantity
#         )
#         db.add(item)

#     await db.commit()
#     await db.refresh(item)
#     return item


# async def remove_cart_item(db, item_id):
#     """
#     Elimina un ítem del carrito.
#     """
#     result = await db.execute(
#         select(CartItem).where(CartItem.id == item_id)
#     )
#     item = result.scalar_one_or_none()

#     if not item:
#         return False

#     await db.delete(item)
#     await db.commit()
#     return True


# async def clear_cart(db: AsyncSession, user_id: int):
#     """
#     Vacía completamente el carrito del usuario.
#     """
#     cart = await get_cart(db, user_id)
#     if not cart:
#         return False

#     await db.execute(
#         delete(CartItem).where(CartItem.cart_id == cart.id)
#     )
#     await db.commit()
#     return True

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cart import Cart, CartItem
from app.models.product import Product


async def get_cart(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Cart).where(Cart.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_cart(db: AsyncSession, user_id: int):
    cart = Cart(user_id=user_id)
    db.add(cart)
    await db.commit()
    await db.refresh(cart)
    return cart


async def add_item(db: AsyncSession, user_id: int, product_id: int, quantity: int):
    if quantity <= 0:
        return None

    # Obtener o crear carrito
    cart = await get_cart(db, user_id)
    if not cart:
        cart = await create_cart(db, user_id)

    # Verificar que el producto existe
    product = (await db.execute(
        select(Product).where(Product.id == product_id)
    )).scalar_one_or_none()

    if not product:
        return None

    # Buscar item existente
    item = (await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
    )).scalar_one_or_none()

    if item:
        item.quantity += quantity
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(item)

    await db.commit()
    await db.refresh(item)
    return item


async def remove_cart_item(db: AsyncSession, user_id: int, item_id: int):
    # Verificar que el item pertenece al carrito del usuario
    cart = await get_cart(db, user_id)
    if not cart:
        return False

    item = (await db.execute(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        )
    )).scalar_one_or_none()

    if not item:
        return False

    await db.delete(item)
    await db.commit()
    return True


async def clear_cart(db: AsyncSession, user_id: int):
    cart = await get_cart(db, user_id)
    if not cart:
        return False

    await db.execute(
        delete(CartItem).where(CartItem.cart_id == cart.id)
    )
    await db.commit()
    return True


# async def update_quantity(db: AsyncSession, item_id: int, new_quantity: int):
#     """
#     Actualiza la cantidad exacta de un item del carrito.
#     """
#     result = await db.execute(
#         select(CartItem).where(CartItem.id == item_id)
#     )
#     item = result.scalar_one_or_none()

#     if not item:
#         return None

#     # Si se pasa new_quantity = 0 → eliminar item
#     if new_quantity <= 0:
#         await db.delete(item)
#         await db.commit()
#         return None

#     # Actualizar
#     item.quantity = new_quantity
#     await db.commit()
#     await db.refresh(item)
#     return item

async def update_quantity(db: AsyncSession, user_id: int, item_id: int, new_quantity: int):

    # Verificar que el item pertenece al usuario
    cart = await get_cart(db, user_id)
    if not cart:
        return None

    result = await db.execute(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        )
    )
    item = result.scalar_one_or_none()

    if not item:
        return None

    # Si la cantidad es 0 → eliminar
    if new_quantity <= 0:
        await db.delete(item)
        await db.commit()
        return None

    item.quantity = new_quantity
    await db.commit()
    await db.refresh(item)
    return item
