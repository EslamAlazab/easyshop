from io import BytesIO
from PIL import Image
import os
import uuid
from fastapi import HTTPException, UploadFile


# Config
SAVE_DIR = "./static/images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


async def save_and_compress_image(image: UploadFile) -> str:
    # Check if the file has a valid extension
    if not allowed_file(image.filename):
        raise HTTPException(status_code=400, detail="Invalid image extension")

    # Check the size of the uploaded file
    contents = await image.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail="File size exceeds the maximum limit of 10 MB")

    # Generate a unique filename using UUID
    extension = image.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4()}.{extension}"

    # Convert the contents to a BytesIO object
    image_file = BytesIO(contents)
    img = Image.open(image_file)

    # Create the full path for the file
    file_path = os.path.join(SAVE_DIR, unique_filename)

    # Compress the image and save it
    img = img.convert("RGB")  # Ensure compatibility with all formats
    img.save(file_path, format='JPEG', optimize=True, quality=85)

    return file_path
