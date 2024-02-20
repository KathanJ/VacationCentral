from fastapi import APIRouter, Request, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from typing import Annotated
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from models.models import Token, TokenData, User, SecureUser

SECRET_KEY = "0660b22db6410c66b6e9356a8cc21536b0ed1f476a161212d772325202a0c57e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    }
}

auth_router = APIRouter()

password_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
oauth2_pwdbearer_flow = OAuth2PasswordBearer(tokenUrl="token")

def get_user(db: dict, username: str | None):
    if username in db:
        user_dict = db[username]
        return SecureUser(**user_dict)
    
def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

def get_hashed_password(plain_password):
    return password_context.hash(plain_password)

def authenticate_user(fakedb: dict, username: str, password: str):
    user = get_user(fakedb, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return False
    else:
        return user
    
def create_access_token(payload: dict, expiration_time : timedelta | None = None):
    if expiration_time:
        expire_at = datetime.now(timezone.utc) + expiration_time
    else:
        expire_at = datetime.now(timezone.utc) + timedelta(seconds=20)
    payload.update({"exp" : expire_at})
    encoded_jwt = jwt.encode(claims=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_pwdbearer_flow)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        jwt_payload = jwt.decode(token = token, key=SECRET_KEY, algorithms=ALGORITHM)
        username : str | None = jwt_payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    current_user = get_user(fake_users_db, username=token_data.username)
    if current_user is None:
        raise credentials_exception
    return current_user

@auth_router.post("/token", response_model=Token)
async def get_token_by_authentication(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Username or Password",
            headers={"WWW-Authenticate" : "Bearer"},
        )
    access_token_expiration_time = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(payload={"sub" : user.username}, expiration_time = access_token_expiration_time)
    return Token(access_token=access_token, token_type="bearer")

@auth_router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user