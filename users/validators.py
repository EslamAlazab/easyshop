from password_validator import PasswordValidator
from database import get_db
from models import User


def username_validator(username: str):
    db = next(get_db())
    errors = []
    if db.query(User).filter(User.username == username).first():
        errors.append('Username used before!')
    return errors


def email_validator(email):
    db = next(get_db())
    errors = []
    if db.query(User).filter(User.email == email).first():
        errors.append('Email used before!')
    return errors


def password_validator(password: str) -> list[str]:
    schema = PasswordValidator
    errors = []

    if not schema().min(8).validate(password):
        errors.append('Password must be at least 8 characters.')
    if not schema().max(50).validate(password):
        errors.append('Password must not exceed 50 characters.')
    if not schema().has().uppercase().validate(password):
        errors.append('Password must contain at least one uppercase letter.')
    if not schema().has().lowercase().validate(password):
        errors.append('Password must contain at least one lowercase letter.')
    if not schema().has().digits().validate(password):
        errors.append('Password must contain at least one digit.')
    if not schema().has().no().spaces().validate(password):
        errors.append('Password must not contain spaces.')
    if not schema().has().symbols().validate(password):
        errors.append('Password must contain at least one symbol.')

    return errors
