# app/routers/product.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from .. import models, schemas
from ..db import get_session

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

# --------------------
# GET /products
# --------------------
@router.get("/", response_model=List[schemas.ProductRead])
async def get_products(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(models.Product))
    products = result.scalars().all()
    return products

# --------------------
# GET /products/{id}
# --------------------
@router.get("/{id}", response_model=schemas.ProductRead)
async def get_product(id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(models.Product).where(models.Product.id == id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# --------------------
# POST /products
# --------------------
@router.post("/", response_model=schemas.ProductRead)
async def create_product(product_in: schemas.ProductCreate, db: AsyncSession = Depends(get_session)):
    db_product = models.Product(**product_in.dict())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product

# --------------------
# PATCH /products/{id}
# --------------------
@router.patch("/{id}", response_model=schemas.ProductRead)
async def patch_product(id: int, product_update: schemas.ProductUpdate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(models.Product).where(models.Product.id == id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return product

# --------------------
# DELETE /products/{id}
# --------------------
@router.delete("/{id}")
async def delete_product(id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(models.Product).where(models.Product.id == id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(product)
    await db.commit()
    return {"detail": "Product deleted successfully"}
