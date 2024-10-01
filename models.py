from sqlalchemy import ForeignKey, TIMESTAMP, String, Numeric, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
from decimal import Decimal


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    password: Mapped[str]
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))

    businesses: Mapped[list['Business']] = relationship(back_populates='owner')


class Business(Base):
    __tablename__ = 'businesses'

    business_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_name: Mapped[str] = mapped_column(String(100), unique=True)
    city: Mapped[str] = mapped_column(String(100), default='Unspecified')
    region: Mapped[str] = mapped_column(String(100), default='Unspecified')
    business_description: Mapped[str | None] = mapped_column(nullable=True)
    logo: Mapped[str] = mapped_column(default='/static/images/default.jpg')

    owner_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))

    owner: Mapped[User] = relationship(back_populates='businesses')
    products: Mapped[list['Product']] = relationship(back_populates='business')


class Product(Base):
    __tablename__ = 'products'

    product_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    category: Mapped[str] = mapped_column(index=True, default='General')
    price: Mapped[float] = mapped_column(Numeric(scale=2))
    discount: Mapped[float | None] = mapped_column(
        Numeric(scale=2), nullable=True, default=None)
    _discounted_price: Mapped[Decimal | None] = mapped_column('discounted_price',
                                                              Numeric(scale=2), nullable=True, default=None)
    offer_expiration_date: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True)
    product_images: Mapped[list[str]] = mapped_column(JSON, default=[])
    date_published: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))

    business_id: Mapped[int] = mapped_column(
        ForeignKey('businesses.business_id'))

    business: Mapped[Business] = relationship(back_populates='products')

    @property
    def discounted_price(self):
        return self._discounted_price

    @discounted_price.setter
    def discounted_price(self, value):
        if value is None:
            self._discounted_price = None
        else:
            self._discounted_price = value
            self.discount = (self.price - self._discounted_price) / \
                self.price * 100 if self.price != 0 else 0
