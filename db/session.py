from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase
from core.config import settings,mongoSettings


SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL  # Retrieve  db_urlfrom configuration settings
engine = create_engine(SQLALCHEMY_DATABASE_URL)   # SQLAlchemy engine creation using specified db_url

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)  # configuring session behavior

MONGODB_URL = mongoSettings.mongo_url    # Get the MongoDB URL from the settings
motor_client = AsyncIOMotorClient(MONGODB_URL)   # Create an instance of AsyncIOMotorClient
mongo_db = motor_client.get_database()    # Reference to the default MongoDB database from the client



# function to get a database session
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

