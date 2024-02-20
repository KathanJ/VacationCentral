from bson import ObjectId
from datetime import date, datetime
from pydantic import FileUrl
from pydantic_core import Url
from fastapi.encoders import jsonable_encoder

# For MongoDB queries
def mongo_compat_conv(dict_obj: dict) -> dict:
    for key,value in dict_obj.items():
        if type(value) is date or type(value) is datetime or type(value) is Url:
            dict_obj[key] = str(value)
    return dict_obj

# For MongoDB responses 
def json_compat_conv(mongo_dict_obj: dict) -> dict:
    for key,value in mongo_dict_obj.items():
        if type(value) is ObjectId:
            mongo_dict_obj[key] = str(value)
        elif type(value) is list:
            for i in range(0,len(value)):
                if type(value[i]) is dict:
                    for k,v in value[i].items():
                        if type(v) is ObjectId:
                            value[i][k] = str(v)
    return mongo_dict_obj