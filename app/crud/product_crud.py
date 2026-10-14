from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate

class ProductCRUD:

    async def create(self, db: AsyncSession, data: ProductCreate):
        new_product = Product(**data.dict())
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return new_product

    async def get_all(self, db: AsyncSession):
        result = await db.execute(select(Product))
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, product_id: int):
        result = await db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def update(self, db: AsyncSession, product_id: int, data: ProductUpdate):
        product = await self.get_by_id(db, product_id)
        if not product:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            setattr(product, key, value)

        await db.commit()
        await db.refresh(product)
        return product

    async def delete(self, db: AsyncSession, product_id: int):
        product = await self.get_by_id(db, product_id)
        if not product:
            return False

        await db.delete(product)
        await db.commit()
        return True


product_crud = ProductCRUD()