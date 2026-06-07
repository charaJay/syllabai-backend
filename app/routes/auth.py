from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.auth import create_access_token
from app.users import find_user, create_user
import bcrypt


router = APIRouter()


class RegisterInput(BaseModel):
    username: str
    password: str

class LoginInput(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(body: RegisterInput):
    if find_user(body.username):
        raise HTTPException(status_code=400, detail="Username already taken.")
    
    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    create_user(body.username, hashed)
    return {"message": "Account created."}


@router.post("/login")
def login(body: LoginInput):
    user = find_user(body.username)
    
    if not user or not bcrypt.checkpw(body.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    token = create_access_token({"sub": body.username})
    return {"access_token": token, "token_type": "bearer"}