from fastapi import APIRouter, HTTPException, status, Path, UploadFile, Body
from .schemas import CreateProduct, UpdateProduct, ReadProduct
from database import db_dependency
from models import Product, Business
from users.auth import user_dependency
from typing import Annotated
from .utils import save_and_compress_image
import os
import datetime


router = APIRouter(prefix='/product', tags=['product'])


@router.get('/')
async def get_all_or_some_product(db: db_dependency, name: str | None = None, category: str | None = None,
                                  price_le: int | None = None, price_ge: int | None = None):
    products = db.query(Product)
    if category:
        products = products.filter(Product.category == category)
    if name:
        products = products.filter(Product.name.ilike(f"%{name}%"))
    if price_le:
        products = products.filter(Product.price <= price_le)
    if price_ge:
        products = products.filter(Product.price >= price_ge)
    return products.all()


@router.get('/{product_id}', response_model=ReadProduct)
async def get_product(product_id: int, user: user_dependency, db: db_dependency):
    product = db.query(Product).filter(Product.product_id == product_id).filter(
        Product.business.has(Business.owner_id == user['id'])).first()
    if not product:
        raise HTTPException(status_code=404, detail=('Product not found!'))
    # add timezone in production
    # if product.offer_expiration_date and product.offer_expiration_date < datetime.datetime.now():
    #     product.offer_expiration_date = None
    #     product.discounted_price = None
    #     product.discount = None
    #     db.commit()
    return product


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_product(product: CreateProduct, user: user_dependency, db: db_dependency):
    business = db.query(Business).filter(
        Business.business_id == product.business_id).filter(Business.owner_id == user['id']).first()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=(
            "Couldn't find the business"))

    product = Product(**product.model_dump())
    db.add(product)
    db.commit()


@router.put('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_product(product_id: Annotated[int, Path(gt=0)], updated_product: UpdateProduct,
                         user: user_dependency, db: db_dependency):
    try:
        product = await get_product(product_id, user, db)
        for key, value in updated_product.model_dump().items():
            if value:
                setattr(product, key, value)
        # if product.discounted_price:
        #     product.discount = (product.price - product.discounted_price) / \
        #         product.price * 100 if product.price != 0 else 0
        db.commit()
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put('/{product_id}/product-images', status_code=status.HTTP_204_NO_CONTENT)
async def add_product_images(product_id: Annotated[int, Path(gt=0)], images: list[UploadFile],
                             user: user_dependency, db: db_dependency):
    try:
        product = await get_product(product_id, user, db)

        # Collect existing images
        all_images = product.product_images.copy() if product.product_images else []
        added_images = []

        for image in images:
            try:
                file_path = await save_and_compress_image(image)
                added_images.append(file_path)
            except HTTPException as e:
                # Clean up any images that were successfully saved before the error
                for path in added_images:
                    os.remove(path)
                raise HTTPException(status_code=e.status_code, detail=f"{
                                    e.detail}, no images added")

        # Update product images if new images were successfully added
        if added_images:
            all_images.extend(added_images)
            product.product_images = all_images
            db.commit()

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        # Handle unexpected exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete('/{product_id}/product-images/')
async def delete_product_images(product_id: Annotated[int, Path(gt=0)], images_path: Annotated[list[str], Body()],
                                user: user_dependency, db: db_dependency):
    try:
        product = await get_product(product_id, user, db)
        images = product.product_images.copy() if product.product_images else []
        for path in images_path:
            try:
                images.remove(path)
                os.remove(path)
            except (ValueError, FileNotFoundError):
                raise HTTPException(
                    status_code=404, detail=f'Could not find "{path}"!')
        product.product_images = images
        db.commit()
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete('/{product_id}')
async def delete_product(product_id: Annotated[int, Path(gt=0)], user: user_dependency,
                         db: db_dependency):
    product_query = db.query(Product).filter(Product.product_id == product_id).filter(
        Product.business.has(Business.owner_id == user['id']))
    if not product_query:
        raise HTTPException(status_code=404, detail=('Product not found!'))
    product_query.delete()
    db.commit()
