from fastapi import FastAPI, status
from routes import routes
from auth import auth
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from dbconfig.dbconfig import db
import random

app = FastAPI()

randlst = []

# @app.middleware("http")
# async def session_middleware(request, call_next):
#     if request.url.path not in ["/", "/login", "/signup"] and not request.url.path.startswith("/static"):
#         session = request.headers.get("session")
#         if session is None:
#             return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
#     response = await call_next(request)
#     return response

# @app.middleware("http")
# async def add_session_middleware(request, call_next):
#     session = request.headers.get("session")
#     if session is None:
#         session_id = random.randint(1,1000)
#         while True:
#             if session_id not in randlst:
#                 session_header = {"session": session_id}
#                 request.headers.update = session_header
#                 randlst.append(session_id)
#                 break
#             else:
#                 session_id = random.randint(1,1000)
        
#     else:
#         session_data = db.Sessions.find()
#     response = await call_next(request)
#     return response

# @app.middleware("http")
# async def redirect_unauthorized_middleware(request, call_next):
#     response = await call_next(request)
#     if response.status_code == 401:
#         response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
#     return response

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(routes.routes_router)
app.include_router(auth.auth_router)