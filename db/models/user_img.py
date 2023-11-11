from motor.motor_asyncio import AsyncIOMotorClient
from core.config import mongoSettings
from fastapi import  Depends

MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "user_data"

# async def get_mongodb():
#     try:
#         MONGO_URI = "mongodb://myUserAdmin:admin123@localhost:27017"
#         # print(MONGO_URI)
#         mongo_client = AsyncIOMotorClient(MONGO_URI)
#         MongoDB = mongo_client["user_data"]
#         MongoProfileCollection = MongoDB["Profile_Picture"]
#         yield MongoProfileCollection
#     except Exception as e:
#         print(str(e))
async def get_mongodb():
    client = AsyncIOMotorClient(MONGODB_URL)
    try:
        # Check if the connection is established
        await client.server_info()
        db = client[DB_NAME]
        yield db
    finally:
        client.close()

# async def get_mongo_profile(user_id: int, db=Depends(get_mongodb)):
#     profile_pic = await db.Profile_Picture.find_one({"user_id": user_id})
#     return profile_pic

async def get_image(user_id: int, db=Depends(get_mongodb)):
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