from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Annotated
from database import db_dependency
from models import Business, Product
from .schemas import CreateBusiness, UpdateBusiness
from users.auth import user_dependency
from sqlalchemy import and_
from .utils import save_and_compress_image
import os

router = APIRouter(prefix='/business', tags=['business'])


@router.get('/')
async def get_all_or_some_businesses(db: db_dependency, business_owner: str | None = None,
                                     city: str | None = None, region: str | None = None):
    businesses = db.query(Business)
    if business_owner:
        businesses = businesses.filter(
            Business.owner.has(username=business_owner))
    if city:
        businesses = businesses.filter(Business.city == city)
    if region:
        businesses = businesses.filter(Business.region == region)
    return businesses.all()


@router.get('/{business_id}')
async def get_business(business_id: int, user: user_dependency, db: db_dependency):
    business = db.query(Business).filter(and_(
        Business.business_id == business_id, Business.owner_id == user['id'])).first()
    if not business:
        raise HTTPException(status_code=404, detail=('Business not found!'))
    return business


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_business(business: CreateBusiness, user: user_dependency, db: db_dependency):
    business = Business(**business.model_dump(), owner_id=user['id'])
    db.add(business)
    db.commit()


@router.put('/{business_id}/logo')
async def update_business_logo(logo: UploadFile, business_id: int, user: user_dependency, db: db_dependency):
    try:
        business = await get_business(business_id=business_id, user=user, db=db)

        old_logo_path = business.logo
        # Save and compress the logo
        try:
            file_path = await save_and_compress_image(logo)
            business.logo = file_path
            db.commit()

            if old_logo_path and os.path.exists(old_logo_path) and old_logo_path != '/static/images/default.jpg':
                os.remove(old_logo_path)

            return {"message": "Business logo updated successfully"}
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_business(updated_business: UpdateBusiness, business_id: int, user: user_dependency, db: db_dependency):
    try:
        business = await get_business(business_id=business_id, user=user, db=db)
        for key, value in updated_business.model_dump().items():
            if value:
                setattr(business, key, value)
            elif key == 'business_description':
                setattr(business, key, None)
        db.commit()
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.delete('/')
async def delete_business(business_id: int, user: user_dependency, db: db_dependency):
    business_query = db.query(Business).filter(and_(
        Business.business_id == business_id, Business.owner_id == user['id']))
    if not business_query:
        raise HTTPException(status_code=404, detail=('Business not found!'))
    business_query.delete()
    db.commit()
