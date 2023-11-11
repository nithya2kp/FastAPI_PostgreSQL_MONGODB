from sqlalchemy.orm import Session
from sqlalchemy import insert,select,update, delete
from fastapi import HTTPException
from schemas.users import UserCreate,UserUpdate
from db.models.users import PostgresProfiles
from core.hashing import Hasher
from motor.motor_asyncio import AsyncIOMotorClient

# mongodb connection
MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "user_data"

# Function to get user by user_id from db
def get_user_by_id(db: Session, user_id: int):
    query = select(PostgresProfiles).where(PostgresProfiles.c.user_id == user_id)
    result = db.execute(query).fetchone()

    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Get column names
    column_names = PostgresProfiles.columns.keys()
    # Convert the result to a dictionary
    user_dict = dict(zip(column_names, result))
    return user_dict

def create_new_user(user:UserCreate,db:Session):
    insert_user = insert(PostgresProfiles).values(
        full_name = user.full_name,
        email =user.email,
        password = Hasher.get_password_hash(user.password),
        phone =user.phone
    )
    print(insert_user)
    result = db.execute(insert_user)
    db.commit()
    return result

def update_user(db: Session, user_id: str, full_name: str = None, password: str = None, phone: str = None, email: str = None):
    # Construct the update statement
    update_stmt = update(PostgresProfiles).where(PostgresProfiles.c.user_id == user_id)

    # Update the specified fields
    if full_name is not None:
        update_stmt = update_stmt.values(full_name=full_name)
    if password is not None:
        update_stmt = update_stmt.values(password=password)
    if phone is not None:
        update_stmt = update_stmt.values(phone=phone)
    if email is not None:
        update_stmt = update_stmt.values(email=email)

    # Execute the update statement
    result = db.execute(update_stmt)

    # Commit the changes
    db.commit()

    # Check if any rows were affected
    if result.rowcount > 0:
        return {"message": "User updated successfully"}
    else:
        return {"message": "User not found"}


def delete_user(db: Session, user_id: int):
    delete_stmt = delete(PostgresProfiles).where(PostgresProfiles.c.user_id == str(user_id))
    result = db.execute(delete_stmt)
    db.commit()

    # Check if any rows were affected
    if result.rowcount > 0:
        return {"message": "User deleted successfully"}
    else:
        return {"message": "User not found"}

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
