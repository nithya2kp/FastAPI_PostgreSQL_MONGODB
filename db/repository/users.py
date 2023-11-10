from sqlalchemy.orm import Session
from  fastapi import HTTPException
from schemas.users import UserCreate,UserUpdate
from db.models.users import PostgresProfiles
from core.hashing import Hasher


# Function to get user by user_id from db
def get_user_by_id(db: Session, id= int):
    return db.query(PostgresProfiles).filter(Users.user_id == id).first()

# Function to create new user in db
def create_new_user(user:UserCreate,db:Session):
    user=PostgresProfiles(
        full_name = user.full_name,
        email =user.email,
        password = Hasher.get_password_hash(user.password),
        phone =user.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

