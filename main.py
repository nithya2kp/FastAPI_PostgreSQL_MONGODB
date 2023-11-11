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
from pymongo import MongoClient
from db.repository.users import get_user_by_id
from db.models.users import get_postgres_db
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorClient

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