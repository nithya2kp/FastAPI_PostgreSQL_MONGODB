from fastapi import  APIRouter,Depends,HTTPException,File,UploadFile,status
from sqlalchemy.orm import Session
from db.models.users import get_postgres_db, get_postgres_profile
from db.models.user_img import get_mongodb,get_image
from schemas.users import UserCreate,UserUpdate,Response,RequestNew
from db.session import get_db
from db.repository.users import create_new_user,get_user_by_id, update_user, delete_user
from typing import Optional, Dict
from db.repository.users import  get_mongo_db
import os


router=APIRouter()

IMAGEDIR = "images/"

@router.post("/")
def create_user( user : UserCreate,db:Session=Depends(get_db)):
    user =create_new_user(user = user,db=db)
    return user

@router.get("/{user_id}")
def get_by_id(user_id: str, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(code=200, status="ok", message="Success get data", result=user).dict(exclude_none=True)

# Endpoint upload image: mongodb
@router.post("/upload/{user_id}")
async def upload_image(user_id: int, file: UploadFile = File(...),postgres_db: Session = Depends(get_postgres_db), db=Depends(get_mongo_db)):
    img_ext = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.tif', '.psd', '.heif', '.heic', '.svg']
    image_data = os.path.splitext(file.filename)

    # Check if the user exists in PostgreSQL
    user_exists = get_user_by_id(postgres_db,user_id)
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in PostgreSQL")

    # images_query = await db.Profile_Picture.find_one({
    #     "profile_picture": image_data[0],
    #     "file_ext": image_data[1],
    #     "user_id": user_id
    # })
    images_query = await db.Profile_Picture.find_one({"user_id": user_id})

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
@router.get("/get_image/{user_id}")
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

@router.get("/get_profile/{user_id}")
async def get_profile(user_id: str,postgres_profile=Depends(get_postgres_profile),mongo_profile=Depends(get_image)):
    if postgres_profile is None and mongo_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_dict = {
        'user_id': postgres_profile.user_id,
        'full_name': postgres_profile.full_name,
        'email': postgres_profile.email,
        'password': postgres_profile.password,
        'phone': postgres_profile.phone
    }

    full_user_data = {**profile_dict, **mongo_profile}
    return full_user_data

@router.delete("/delete")
def delete_user_details(user_id: int, db: Session = Depends(get_db)):
    result = delete_user(db, user_id=user_id)
    return Response(code=200, status="ok", message=result["message"], result=None).dict(exclude_none=True)


@router.post("/update")
def update_user_details(request: RequestNew,db:Session = Depends(get_db)):
    _user = update_user(db,user_id=request.parameter.user_id,full_name=request.parameter.full_name,password=request.parameter.password,phone=request.parameter.phone,email=request.parameter.email)
    return Response(code=200,status="ok",message="Success update data",result=_user)




