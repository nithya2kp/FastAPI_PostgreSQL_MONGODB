#main.py
from db.session import engine
from db.base_class import Base
from fastapi import FastAPI,File,UploadFile,HTTPException,Depends,status,Request
from fastapi.responses import StreamingResponse
from apis.base import route_users
from db import models
import os
from io import BytesIO
from PIL import Image
from bson import ObjectId
from core.config import settings,mongoSettings
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)

# For storing images
IMAGEDIR = "images/"
def create_tables():
    Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    create_tables()
    return app


app = start_application()


@app.get("/")
def hello_api():
    return {"msg":"Hello FastAPI🚀"}

# Including the user routes
app.include_router(route_users.router,prefix="",tags=["users"])

# db parameters postgresql
b_params = {
    "dbname": "python_db2",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432",
}

# posgresql db connection
def create_connection():
    conn = psycopg2.connect(**db_params)
    curr = conn.cursor()
    return conn, curr

# mongodb connection
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "user_data"
IMAGEDIR = "images/"

# AsyncIOMotorClient for mongodb
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]

# Function for mongodb connection
async def get_mongo_db():
    client = AsyncIOMotorClient(MONGODB_URL)
    try:
        # Check if the connection is established
        await client.server_info()
        db = client[DB_NAME]
        yield db
    finally:
        client.close()

# Endpoint upload image: mongodb
@app.post("/upload/{user_id}")
async def upload_image(user_id: int, file: UploadFile = File(...), db=Depends(get_mongo_db)):
    img_ext = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.tif', '.psd', '.heif', '.heic', '.svg']
    image_data = os.path.splitext(file.filename)

    images_query = await db.Profile_Picture.find_one({
        "profile_picture": image_data[0],
        "file_ext": image_data[1],
        "user_id": user_id
    })

    if not images_query:
        data = {
            "profile_picture": image_data[0],
            "user_id": user_id,
            "file_ext": image_data[1],
            "contents": await file.read()
        }

        add_query = await db.Profile_Picture.insert_one(data)

        file.filename = image_data
        with open(IMAGEDIR + str(image_data[0]) + str(image_data[1]), "wb") as f:
            f.write(data["contents"])

        return {"filename": file.filename}
    else:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, detail="This image already exists for the user")

# Endpoint get image : mongodb

@app.get("/get_image/{user_id}")
async def get_image(user_id: int, db=Depends(get_mongo_db)):
    try:
        user = await db.Profile_Picture.find_one({"user_id": user_id})
        if user:
            image_data = user.get("profile_picture")
            if image_data:
                return {"image_data": image_data}
            else:
                raise HTTPException(status_code=404, detail="Image not found for the user")
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

