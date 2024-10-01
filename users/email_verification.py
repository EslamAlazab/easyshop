from fastapi.templating import Jinja2Templates
from fastapi import Request
import aiosmtplib
from email.message import EmailMessage
import os
from .auth import gen_token
from models import User
from datetime import timedelta


templates = Jinja2Templates(directory="templates")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")


async def email_verify(user, request, db):
    token = gen_token(user['id'], user['username'], timedelta(hours=2))

    useremail = db.query(User).filter(User.user_id == user['id']).first().email
    template = templates.get_template(
        'verification_email.html').render({'request': request, 'token': token})
    message = EmailMessage()
    message["From"] = FROM_EMAIL
    message["To"] = useremail
    message["Subject"] = 'EasyShopas Account Verification'
    message.add_alternative(template, subtype='html')

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        use_tls=True,
    )
