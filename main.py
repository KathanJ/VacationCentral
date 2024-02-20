from fastapi import FastAPI
from routes import routes
from auth import auth
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(routes.routes_router)
app.include_router(auth.auth_router)