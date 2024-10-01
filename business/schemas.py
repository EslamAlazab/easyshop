from pydantic import BaseModel, Field, field_validator
from database import get_db
from models import Business
import datetime
from typing import Optional


def name_validator(name: str):
    db = next(get_db())
    errors = []
    if db.query(Business).filter(Business.business_name == name).first():
        errors.append('Business name used before!')
    return errors


class CreateBusiness(BaseModel):
    business_name: str = Field(max_length=100)
    city: str = Field(max_length=100, default='Unspecified')
    region: str = Field(max_length=100, default='Unspecified')
    business_description: str | None = None

    @field_validator('business_name')
    def name_validation(cls, name: str):
        errors = name_validator(name)
        if errors:
            raise ValueError(f'Invalid business name: {", ".join(errors)}')
        return name


class UpdateBusiness(BaseModel):
    business_name: str | None = Field(max_length=100, default=None)
    city: str | None = Field(max_length=100, default=None)
    region: str | None = Field(max_length=100, default=None)
    business_description: str | None = None

    @field_validator('business_name')
    def name_validation(cls, name: str):
        if not name or name.isspace():
            return None

        errors = name_validator(name)
        if errors:
            raise ValueError(f'Invalid business name: {", ".join(errors)}')
        return name


class CreateProduct(BaseModel):
    name: str = Field(max_length=100)
    category: str = Field(max_length=200, default='General')
    price: float = 0.00
    business_id: int


class UpdateProduct(BaseModel):
    name: str | None = Field(max_length=100, default=None)
    category: str = Field(max_length=200, default=None)
    price: Optional[float] = None
    discounted_price: Optional[float] = None
    offer_expiration_date: Optional[datetime.datetime] = None


class ReadProduct(BaseModel):
    product_id: int
    name: str
    category: str
    price: float
    offer_expiration_date: datetime.datetime | None
    discounted_price: float | None
    discount: float | None
    product_images: list[str]
    date_published: datetime.datetime

    class Config:
        from_attributes = True
