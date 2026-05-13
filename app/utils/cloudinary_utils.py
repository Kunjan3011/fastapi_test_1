import os

import cloudinary
from cloudinary.uploader import upload
from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException
from starlette import status

load_dotenv()
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


async def upload_to_cloudinary(image: UploadFile):
    max_size = 5 * 1024 * 1024
    content_types = ["image/png", "image/jpeg"]

    if image.content_type not in content_types:
        raise HTTPException(status_code=415, detail="Only PNG and JPEG images are allowed")

    if image.size > max_size:
        raise HTTPException(status_code=400, detail="File size not valid")

    try:
        upload_result = upload(image.file, asset_folder="task_management_system")
        return upload_result["secure_url"]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cloudinary upload failed")
