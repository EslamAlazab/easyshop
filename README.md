# EasyShop

EasyShop is a simple API practice project built using FastAPI. It consists of two main applications: Users and Business.

## Apps Overview

- Users App: Manages user registration, authentication, and user-related data.
- Business App: Handles CRUD operations for businesses owned by users, with each user being able to manage multiple businesses. It also manages products associated with each business.

## Key Features

- JWT Authentication: Secure user authentication with JSON Web Tokens (JWT).
- Email Verification: Users receive an email verification link to activate their account.
- Image Uploads:
  - Upload product images or business logos.
  - Ensure the uploaded file is a valid image.
  - Restrict file size and compress images.
- Search and Filtering:
  - Search for businesses or products.
  - Apply filters to refine search results.

## Tools & Technologies

- FastAPI: High-performance API framework.
- SQLAlchemy: SQL toolkit and Object-Relational Mapping (ORM).
- Pydantic v2: Data validation and settings management using Python type hints.
- Passlib & Bcrypt: Password hashing for secure authentication.
- aiosmtplib: Asynchronous email sending for user verification.
- Jinja2: Templating engine for rendering HTML emails and responses.
