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

# @routes_router.get('/')
# async def home():
#     return "Hello World"

@routes_router.get("/", response_class=HTMLResponse)
async def get_landing(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )

@routes_router.get("/login", response_class=HTMLResponse)
async def get_login(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="login.html", context={}
    )

# @routes_router.post("/login")
# async def post_login(username: Annotated[str, Form()], password: Annotated[str, Form()]) -> str | None:
#     return username

@routes_router.get("/signup", response_class=HTMLResponse)
async def get_signup(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="signup.html", context={}
    )

dummy_post_objs = [
    {"user" : "KathanJani2803", "img" : "img/post_img_2.png", "community": {"img" : "img/vclogo-white.svg", "name" : "vc/Community2"}, "title" : "Statue Of Unity", "desc" : "dummy description 2", "posted_at" : "It's been 84 years...", "tags": ["#Gujarat","#HotelBRGBudgetStay","#SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "comments": 12},
    {"user" : "HarshAwasthi1204", "img" : "img/post_img_1.png", "community": {"img" : "img/vclogo.svg", "name" : "vc/Community1"}, "title" : "Taj Mahal", "desc" : "dummy description 1", "posted_at" : "A millenium ago...", "tags": ["#Agra","#TajMahalPalaceHotel","#MehtabBagh"], "likes": 100, "dislikes": 50, "comments": 25},
    {"user" : "PriyankaJavani2310", "img" : "img/post_img_3.png", "community": {"img" : "img/vclogo.svg", "name" : "vc/Community3"}, "title" : "Qutub Minar", "desc" : "dummy description 3", "posted_at" : "??? years ago...", "tags": ["#Delhi","#QutubResidencyHotel","#QutubMinarPark"], "likes": 50, "dislikes": 10, "comments": 4},
    {"user" : "KathanJani2803", "img" : "img/post_img_2.png", "community": {"img" : "img/vclogo-white.svg", "name" : "vc/Community2"}, "title" : "Statue Of Unity", "desc" : "dummy description 2", "posted_at" : "It's been 84 years...", "tags": ["#Gujarat","#HotelBRGBudgetStay","#SardarPatelZoologicalPark"], "likes": 25, "dislikes": 10, "comments": 12},
    {"user" : "HarshAwasthi1204", "img" : "img/post_img_1.png", "community": {"img" : "img/vclogo.svg", "name" : "vc/Community1"}, "title" : "Taj Mahal", "desc" : "dummy description 1", "posted_at" : "A millenium ago...", "tags": ["#Agra","#TajMahalPalaceHotel","#MehtabBagh"], "likes": 100, "dislikes": 50, "comments": 25},
    {"user" : "PriyankaJavani2310", "img" : "img/post_img_3.png", "community": {"img" : "img/vclogo.svg", "name" : "vc/Community3"}, "title" : "Qutub Minar", "desc" : "dummy description 3", "posted_at" : "??? years ago...", "tags": ["#Delhi","#QutubResidencyHotel","#QutubMinarPark"], "likes": 50, "dislikes": 10, "comments": 4},
]

dummy_recent_search_objs = [
    {"img" : "img/dummy_search_img_1.jpg", "name" : "Thar Desert", "place" : "Rajasthan & Gujarat"},
    {"img" : "img/dummy_search_img_2.jpg", "name" : "Red Fort", "place" : "Delhi"},
    {"img" : "img/dummy_search_img_3.jpg", "name" : "Golden Temple", "place" : "Punjab"},
]

now = datetime.now()
dummy_trending_objs = [
    {"name" : "Thar Desert", "place" : "Rajasthan & Gujarat", "day" : now.day, "month": now.strftime('%b').upper()},
    {"name" : "Red Fort", "place" : "Delhi", "day" : now.day, "month": now.strftime('%b').upper()},
    {"name" : "Golden Temple", "place" : "Punjab", "day" : now.day, "month": now.strftime('%b').upper()},
]

dummy_followed_communities_objs = [
    {"img" : "img/vclogo.svg", "name" : "vc/Community1"},
    {"img" : "img/vclogo-white.svg", "name" : "vc/Community2"},
    {"img" : "img/vclogo.svg", "name" : "vc/Community3"},
]

dob=datetime(2004,3,28)
dummy_user_dict = {
    "username" : "KathanJani2803", "name": "Kathan Jani", "bio":"I don't know where I'm going, but I'm on my way.", "user_id" : "1234567890", "profile_pic" : "img/generic_pfp.png",
    "emailid": "kj2803@gmail.com", "region":"Asia", "contactno": "1234567890", "dob":dob.strftime("%Y-%m-%d"), "gender":"Male",
    "posts": dummy_post_objs, "recent_searches": dummy_recent_search_objs, "recent_searches_count": len(dummy_recent_search_objs),
    "trending": dummy_trending_objs, "trending_count": len(dummy_trending_objs), "followed_communities": dummy_followed_communities_objs,
    "followed_communities_count": len(dummy_followed_communities_objs), "search_suggestions": ["Thar Desert", "Red Fort", "Golden Temple"],
    "location":"Gandhinagar", "birthdate":str(dob.strftime('%b'))+' '+str(dob.day)+', '+str(dob.year), "post_count": len(list(x for x in dummy_post_objs if x["user"] == "KathanJani2803")), "points": 1000
}

dummy_user_dict1 = {
    "username" : "KathanJani2803", "name": "Kathan Jani", "bio":"I don't know where I'm going, but I'm on my way.", "user_id" : "1234567890", "profile_pic" : "img/generic_pfp.png",
    "emailid": "kj2803@gmail.com", "region":"Asia", "contactno": "1234567890", "dob":dob.strftime("%Y-%m-%d"), "gender":"Male",
    "posts": [dummy_post_objs[i:i+3] for i in range(0, len(dummy_post_objs), 3)], "recent_searches": dummy_recent_search_objs, "recent_searches_count": len(dummy_recent_search_objs),
    "trending": dummy_trending_objs, "trending_count": len(dummy_trending_objs), "followed_communities": dummy_followed_communities_objs,
    "followed_communities_count": len(dummy_followed_communities_objs), "search_suggestions": ["Thar Desert", "Red Fort", "Golden Temple"],
    "location":"Gandhinagar", "birthdate":str(dob.strftime('%b'))+' '+str(dob.day)+', '+str(dob.year), "post_count": len(list(x for x in dummy_post_objs if x["user"] == "KathanJani2803")), "points": 1000
}
dob2=datetime(2003,4,12)
dummy_user_dict2 = {
    "username" : "KathanJani2803", "name": "Harsh Awasthi", "bio":"I don't know where I'm going, but I'm on my way.", "user_id" : "1204", "profile_pic" : "img/generic_pfp.png",
    "emailid": "ha1204@gmail.com", "region":"Asia", "contactno": "1234567890", "dob":dob2.strftime("%Y-%m-%d"), "gender":"Male",
    "posts": dummy_post_objs, "recent_searches": dummy_recent_search_objs, "recent_searches_count": len(dummy_recent_search_objs),
    "trending": dummy_trending_objs, "trending_count": len(dummy_trending_objs), "followed_communities": dummy_followed_communities_objs,
    "followed_communities_count": len(dummy_followed_communities_objs), "search_suggestions": ["Thar Desert", "Red Fort", "Golden Temple"],
    "location":"Ahmedabad", "birthdate":str(dob2.strftime('%b'))+' '+str(dob2.day)+', '+str(dob2.year), "post_count": len(list(x for x in dummy_post_objs if x["user"] == "HarshAwasthi1204")), "points": 1000
}
dob3=datetime(2003,10,23)
dummy_user_dict3 = {
    "username" : "KathanJani2803", "name": "Priyanka Javani", "bio":"I don't know where I'm going, but I'm on my way.", "user_id" : "2310", "profile_pic" : "img/generic_pfp.png",
    "emailid": "pj2310@gmail.com", "region":"Asia", "contactno": "1234567890", "dob":dob3.strftime("%Y-%m-%d"), "gender":"Female",
    "posts": dummy_post_objs, "recent_searches": dummy_recent_search_objs, "recent_searches_count": len(dummy_recent_search_objs),
    "trending": dummy_trending_objs, "trending_count": len(dummy_trending_objs), "followed_communities": dummy_followed_communities_objs,
    "followed_communities_count": len(dummy_followed_communities_objs), "search_suggestions": ["Thar Desert", "Red Fort", "Golden Temple"],
    "location":"Ahmedabad", "birthdate":str(dob3.strftime('%b'))+' '+str(dob3.day)+', '+str(dob3.year), "post_count": len(list(x for x in dummy_post_objs if x["user"] == "PriyankaJavani2310")), "points": 1000
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

@routes_router.get("/searchresults", response_class=HTMLResponse)
async def get_searchresults(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="searchresults.html", context={
            "status":True,"user":dummy_user_dict1
        }
    )

@routes_router.get("/discussionthread", response_class=HTMLResponse)
async def get_discussionthread(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="discussionthread.html", context={
            "status":True,"user":dummy_user_dict, "post":dummy_post_objs[0]
        }
    )

@routes_router.get("/faqs", response_class=HTMLResponse)
async def get_faqs(request : Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request, name="faqs.html", context={
            "status":True,"user":dummy_user_dict
        }
    )

@routes_router.get("/profile/{username}/{tab}", response_class=HTMLResponse)
async def get_profile(request : Request, tab : str, username : str) -> HTMLResponse:
    if username == "KathanJani2803":
        userdict = dummy_user_dict
    elif username == "HarshAwasthi1204":
        userdict = dummy_user_dict2
    elif username == "PriyankaJavani2310":
        userdict = dummy_user_dict3
    return templates.TemplateResponse(
        request=request, name="profile.html", context={
            "status":True,"user":userdict, "tab":tab, "username":username
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