from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductUpdate
from app.crud.product_crud import product_crud
from app.api.routes_auth import get_current_active_user
from app.core.auth import require_role
from app.core.upload_image import upload_image_to_cloudinary, delete_image_from_cloudinary
from typing import Optional

router = APIRouter(prefix="/products", tags=["Products"])


# ---------------- OBTENER todo (público) ----------------
@router.get("/", response_model=list[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    return await product_crud.get_all(db)


# ---------------- OBTENER por ID (público) ----------------
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await product_crud.get_by_id(db, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    return product


# ---------------- CREAR (solo admin) ----------------
@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin"))
):
    return await product_crud.create(db, data)


# ---------------- ACTUALIZAR (solo admin) ----------------
@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin"))
):
    product = await product_crud.update(db, product_id, data)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    return product


# ---------------- ELIMINAR (solo admin) ----------------
@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin"))
):
    product = await product_crud.get_by_id(db, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    # Eliminar imagen de Cloudinary si existe
    if product.image:
        await delete_image_from_cloudinary(product.image)
    ok = await product_crud.delete(db, product_id)
    if not ok:
        raise HTTPException(404, "Producto no encontrado")
    return




# ---------------- SUBIR IMAGEN (solo admin) ----------------
@router.post("/upload-image", status_code=200)
async def upload_product_image(
    file: UploadFile = File(...),
    user=Depends(require_role("admin"))
):
    """
    Sube una imagen a Cloudinary y retorna la URL.
    Usar este endpoint desde Flutter antes de crear/actualizar un producto.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "El archivo debe ser una imagen")
    
    image_url = await upload_image_to_cloudinary(file, folder="products")
    return {"image_url": image_url}

# ---------------- ACTUALIZAR IMAGEN DE PRODUCTO (solo admin) ----------------
@router.put("/{product_id}/update-image", status_code=200)
async def update_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin"))
):
    """
    Actualiza solo la imagen de un producto existente.
    Elimina la imagen anterior de Cloudinary si existe.
    """
    product = await product_crud.get_by_id(db, product_id)
    if not product:
        raise HTTPException(404, "Producto no encontrado")
    
    # Eliminar imagen anterior si existe
    if product.image:
        await delete_image_from_cloudinary(product.image)
    
    # Subir nueva imagen
    image_url = await upload_image_to_cloudinary(file, folder="products")
    
    return {"image_url": image_url}
    