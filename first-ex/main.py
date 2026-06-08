from fastapi import FastAPI
from config import get_settings
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from auth_utils import create_access_token, verify_token

config = get_settings()

app = FastAPI(title="Resume Evaluator API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = "user"

fake_users_db = {
    "admin": {"username": "admin", "password": "12345", "email": "admin@example.com", "role": "admin", "department": "Administration"},
    "user": {"username": "user1", "password": "12345", "email": "user@example.com", "role": "user", "department": "User Experience"},
    "manager": {"username": "Bob", "password": "12345", "email": "user@example.com", "role": "manager"},
    "finance": {"username": "Bob", "password": "12345", "email": "user@example.com", "role": "finance"},
}

def authenticate_user(username: str, password: str) -> Optional[User]:
    user = fake_users_db.get(username)
    if not user or user["password"] != password:
        return None
    return User(username=user["username"], email=user.get("email"), role=user.get("role", "user"))


@app.get("/")
def root():
    return {"message": "Resume Evaluator API is running"}

@app.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username, "role": user.role}, expires_delta=None)
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = fake_users_db.get(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return User(username=user["username"], email=user.get("email"), role=user.get("role", "user"))

def require_user(user: User = Depends(get_current_user)):
    if user.role != "user" and user.role != "admin" and user.role != "manager" and user.role != "finance":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user


@app.get("/profile")
def jwt_profile(user: User = Depends(require_user)):
    return user

@app.get("/admin")
def jwt_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user
