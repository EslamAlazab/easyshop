
from pydantic import BaseModel, Field, EmailStr, field_validator
from .auth import bcrypt_context
from .validators import password_validator, email_validator, username_validator


class UserRequest(BaseModel):
    username: str = Field(max_length=50)
    email: EmailStr = Field(max_length=200)
    password: str

    class Config:
        from_attributes = True

    @field_validator('username')
    def validate_username(cls, username: str):
        errors = username_validator(username)
        if errors:
            raise ValueError(f'Invalid username: {", ".join(errors)}')
        return username

    @field_validator('email')
    def validate_email(cls, email: str):
        errors = email_validator(email)
        if errors:
            raise ValueError(f'Invalid email: {", ".join(errors)}')
        return email

    @field_validator('password')
    def hash_password(cls, password: str):
        errors = password_validator(password)
        if errors:
            raise ValueError(f'Invalid password: {", ".join(errors)}')
        return bcrypt_context.hash(password)


class Token(BaseModel):
    access_token: str
    token_type: str
