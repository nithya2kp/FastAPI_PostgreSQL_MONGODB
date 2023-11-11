from sqlalchemy import create_engine,Column,String,Integer,MetaData,Table
from db.base_class import Base
from sqlalchemy.orm import sessionmaker
from core.config import Settings
from fastapi import Depends

metadata = MetaData()
postgres_engine = create_engine(Settings.DATABASE_URL)

PostgresProfiles = Table(
    "users",
    metadata,
    Column("user_id", String),
    Column("full_name", String),
    Column("email",String,nullable=False, unique=True, index=True),
    Column("password",String,nullable=False),
    Column("phone",String, nullable=False,unique=True)
)

# Function to connect to PostgreSQL database
def get_postgres_db():
    db = postgres_engine.connect()
    try:
        yield db
    finally:
        db.close()

async def get_postgres_profile(user_id: str, db=Depends(get_postgres_db)):
    query = PostgresProfiles.select().where(PostgresProfiles.c.user_id == user_id)
    return db.execute(query).fetchone()