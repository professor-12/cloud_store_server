from dotenv import load_dotenv


import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api

load_dotenv()

config = cloudinary.config(secure=True)

def uploadImage(image:any) -> str:
  url = cloudinary.uploader.upload(image,  unique_filename = False, overwrite=True,asset_folder="media/profile_pictures")
  return url.get("secure_url")


