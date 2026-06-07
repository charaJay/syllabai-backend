from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth import get_current_user
from app.users import find_user, update_user
from app.crypto import encrypt, decrypt

router = APIRouter()


class ApiKeyInput(BaseModel):
    api_key: str


@router.get("/me")
def get_me(username: str = Depends(get_current_user)):
    user = find_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {
        "username": user["username"],
        "has_api_key": user["api_key"] is not None,
        "conversations": user["conversations"]
    }


@router.post("/api-key")
def save_api_key(body: ApiKeyInput, username: str = Depends(get_current_user)):
    user = find_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user["api_key"] = encrypt(body.api_key)
    update_user(username, user)
    return {"message": "API key saved."}


@router.delete("/api-key")
def delete_api_key(username: str = Depends(get_current_user)):
    user = find_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user["api_key"] = None
    update_user(username, user)
    return {"message": "API key deleted."}


@router.get("/api-key/verify")
def verify_api_key(username: str = Depends(get_current_user)):
    user = find_user(username)
    if not user or not user["api_key"]:
        raise HTTPException(status_code=404, detail="No API key found.")
    
    try:
        decrypt(user["api_key"])
        return {"message": "API key is valid."}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to decrypt API key.")


@router.delete("/conversations")
def clear_conversations(username: str = Depends(get_current_user)):
    user = find_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user["conversations"] = []
    update_user(username, user)
    return {"message": "Conversations cleared."}