from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from auth.auth import get_token_by_authentication
from auth.hashers import pwd_hasher
from models.models import User, UnsecuredUser, SecureUser
from models.converters import mongo_compat_conv, json_compat_conv
from dbconfig.dbconfig import db
import json
from bson import ObjectId

from datetime import datetime

routes_router = APIRouter()

templates = Jinja2Templates(directory = "templates")

@routes_router.get('/')
async def home():
    return "Hello World"

@routes_router.get("/login", response_class=HTMLResponse)
async def get_login(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="login.html", context={}
    )

@routes_router.post("/login")
async def post_login(username: Annotated[str, Form()], password: Annotated[str, Form()]) -> str | None:
    return username

@routes_router.get("/signup", response_class=HTMLResponse)
async def get_signup(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="signup.html", context={}
    )

dummy_post_objs = [
    {"user" : "Kathan Jani", "img" : "static/img/post_img_2.png", "thread": {"img" : "static/img/vclogo-white.svg", "name" : "t/Thread2"}, "title" : "Statue Of Unity", "desc" : "dummy description 2", "posted_at" : "It's been 84 years...", "tags": ["#Gujarat","#HotelBRGBudgetStay","#SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "comments": 12},
    {"user" : "Harsh Awasthi", "img" : "static/img/post_img_1.png", "thread": {"img" : "static/img/vclogo.svg", "name" : "t/Thread1"}, "title" : "Taj Mahal", "desc" : "dummy description 1", "posted_at" : "A millenium ago...", "tags": ["#Agra","#TajMahalPalaceHotel","#MehtabBagh"], "likes": 100, "dislikes": 50, "comments": 25},
    {"user" : "Priyanka Javani", "img" : "static/img/post_img_3.png", "thread": {"img" : "static/img/vclogo.svg", "name" : "t/Thread3"}, "title" : "Qutub Minar", "desc" : "dummy description 3", "posted_at" : "??? years ago...", "tags": ["#Delhi","#QutubResidencyHotel","#QutubMinarPark"], "likes": 50, "dislikes": 10, "comments": 4},
    
]

dummy_recent_search_objs = [
    {"img" : "static/img/dummy_search_img_1.jpg", "name" : "Thar Desert", "place" : "Rajasthan & Gujarat"},
    {"img" : "static/img/dummy_search_img_2.jpg", "name" : "Red Fort", "place" : "Delhi"},
    {"img" : "static/img/dummy_search_img_3.jpg", "name" : "Golden Temple", "place" : "Punjab"},
]

now = datetime.now()
dummy_trending_objs = [
    {"name" : "Thar Desert", "place" : "Rajasthan & Gujarat", "day" : now.day, "month": now.strftime('%b').upper()},
    {"name" : "Red Fort", "place" : "Delhi", "day" : now.day, "month": now.strftime('%b').upper()},
    {"name" : "Golden Temple", "place" : "Punjab", "day" : now.day, "month": now.strftime('%b').upper()},
]

dummy_followed_threads_objs = [
    {"img" : "static/img/vclogo.svg", "name" : "t/Thread1"},
    {"img" : "static/img/vclogo-white.svg", "name" : "t/Thread2"},
    {"img" : "static/img/vclogo.svg", "name" : "t/Thread3"},
]

dummy_user_dict = {
    "username" : "Kathan Jani", "user_id" : "1234567890", "profile_pic" : "static/img/generic_pfp.png",
    "posts": dummy_post_objs, "recent_searches": dummy_recent_search_objs, "recent_searches_count": len(dummy_recent_search_objs),
    "trending": dummy_trending_objs, "trending_count": len(dummy_trending_objs), "followed_threads": dummy_followed_threads_objs,
    "followed_threads_count": len(dummy_followed_threads_objs)
}

@routes_router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="dashboard.html", context={
            "status":True, "user":dummy_user_dict
        }
    )

@routes_router.get("/help", response_class=HTMLResponse)
async def get_help(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="help.html", context={
            "status":True,"user":dummy_user_dict
        }
    )

#User CRUD Endpoints
@routes_router.post("/createuser/", status_code=201, response_class=JSONResponse)
async def create_user(register_user: UnsecuredUser) -> JSONResponse:
    create_user_check = db.Users.find_one({"username" : register_user.username})
    if create_user_check:
        return JSONResponse({"message" : "User Already Exists"},status_code=409)
    user_dict = register_user.model_dump()
    # if user_dict:
        # print(type(user_dict['dob']))
        # user_dict['dob'] = str(user_dict['dob'])
        # print(type(user_dict['created_at']))
        # user_dict['created_at'] = str(user_dict['created_at'])
        # print(type(user_dict['aadhar_card']))
        # user_dict['aadhar_card'] = str(user_dict['aadhar_card'])
        # user_dict["user_id"] = str(user_dict["user_id"])
    create_hashed_pwd = pwd_hasher(user_dict["password"])
    create_secure_user_dict = SecureUser(**user_dict, hashed_password=create_hashed_pwd).model_dump()
    mongo_compat_create_user_dict = mongo_compat_conv(create_secure_user_dict)
    create_user_query = db.Users.insert_one(mongo_compat_create_user_dict)
    if not create_user_query:
        return JSONResponse({"message" : "Internal Server Error"},status_code=500)
    update_userid_query = db.Users.update_one({"_id": create_user_query.inserted_id}, {"$set": {"user_id": create_user_query.inserted_id}})
    if not update_userid_query:
        return JSONResponse({"message" : "Internal Server Error"},status_code=500)
    return JSONResponse(content={"message" : "User Successfully Created", "user_id" : str(create_user_query.inserted_id)})

@routes_router.get("/readuser/{username}", status_code=200, response_model= User)
async def read_user(username: str) -> User | JSONResponse:
    read_user_query = db.Users.find_one({"username": username})
    if not read_user_query:
        return JSONResponse(content={"message" : "User Not Found"},status_code=404)
    else:
        read_user_query = json_compat_conv(read_user_query)
    # return JSONResponse(content=read_user_query)
    return User(**read_user_query)

@routes_router.put("/updateuser/{username}", status_code=200, response_class=JSONResponse)
async def update_user(username: str, update_user_data: UnsecuredUser) -> JSONResponse:
    update_user_check = db.Users.find_one({"username" : username})
    if not update_user_check:
        return JSONResponse(content={"message" : "User Not Found"},status_code=404)
    update_user_data_dict = update_user_data.model_dump(exclude_unset=True)
    if pwd_hasher(update_user_data_dict["password"]) != update_user_check["hashed_password"]:
        update_hashed_pwd = pwd_hasher(update_user_data_dict["password"])
        update_secure_user_dict = SecureUser(**update_user_data_dict, hashed_password=update_hashed_pwd).model_dump(exclude_unset=True)
    else:
        update_secure_user_dict = SecureUser(**update_user_data_dict, hashed_password=update_user_check["hashed_password"]).model_dump(exclude_unset=True)
    mongo_compat_update_user_dict = mongo_compat_conv(update_secure_user_dict)
    update_user_query = db.Users.update_one({"username": username}, {"$set": mongo_compat_update_user_dict})
    if not update_user_query:
        return JSONResponse({"message" : "Internal Server Error"},status_code=500)
    return JSONResponse(content={"message" : "User Successfully Updated", "user_id" : str(update_user_check["_id"])})

@routes_router.delete("/deleteuser/{username}", status_code=200, response_class=JSONResponse)
async def delete_user(username: str, password: str) -> JSONResponse:
    delete_user_check = db.Users.find_one({"username" : username})
    if not delete_user_check:
        return JSONResponse(content={"message" : "User Not Found"},status_code=404)
    if pwd_hasher(password) != delete_user_check["hashed_password"]:
        return JSONResponse(content={"message" : "Invalid Password"},status_code=401)
    find_following_users_query = db.Users.find({"followers.user_id": delete_user_check["_id"]})
    for following_users in find_following_users_query:
        for user in following_users["followers"]:
            if user["user_id"] == delete_user_check["_id"]:
                following_users["followers"].remove(user)
        update_following_users_query = db.Users.update_one({"_id": following_users["_id"]}, {"$set": {"followers": following_users["followers"]}})
    delete_user_query = db.Users.delete_one({"username": username})
    if not delete_user_query or not update_following_users_query:
        return JSONResponse({"message" : "Internal Server Error"},status_code=500)
    return JSONResponse(content={"message" : "User Successfully Deleted", "deleted_user_id" : str(delete_user_check["_id"])})