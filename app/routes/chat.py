import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.auth import get_current_user
from app.users import find_user, get_notebook, update_notebook
from app.crypto import decrypt
from app.openai import stream_chat

router = APIRouter()

class ChatInput(BaseModel):
    notebook_id: str
    topic: str
    message: str
    history: list[dict] = []

@router.post("/")
def chat(body: ChatInput, username: str = Depends(get_current_user)):
    user = find_user(username)
    if not user or not user["api_key"]:
        raise HTTPException(status_code=400, detail="No API key set.")

    notebook = get_notebook(username, body.notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found.")

    api_key = decrypt(user["api_key"])

    messages = [
        {
            "role": "system",
            "content": f"You are a helpful tutor explaining the topic '{body.topic}' to a student. Be clear, concise, and academic."
        }
    ] + body.history + [
        {"role": "user", "content": body.message}
    ]

    def generate():
        full_response = ""
        for chunk in stream_chat(api_key, messages):
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                yield delta

        # save to notebook conversations
        notebook_fresh = get_notebook(username, body.notebook_id)
        conversations = notebook_fresh.get("conversations", {})
        existing = conversations.get(body.topic, [])

        if body.history:
            updated = body.history + [
                {"role": "user", "content": body.message},
                {"role": "assistant", "content": full_response}
            ]
        else:
            updated = [
                {"role": "user", "content": body.message},
                {"role": "assistant", "content": full_response}
            ]

        conversations[body.topic] = updated
        update_notebook(username, body.notebook_id, {"conversations": conversations})

    return StreamingResponse(generate(), media_type="text/plain")