import fitz
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from app.auth import get_current_user
from app.users import find_user, update_notebook, get_notebook
from app.crypto import decrypt
from app.openai import extract_topics, generate_checklist

router = APIRouter()

@router.post("/{notebook_id}/upload")
async def upload_syllabus(
    notebook_id: str,
    file: UploadFile = File(...),
    username: str = Depends(get_current_user)
):
    user = find_user(username)
    if not user or not user["api_key"]:
        raise HTTPException(status_code=400, detail="No API key set.")

    notebook = get_notebook(username, notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found.")

    api_key = decrypt(user["api_key"])

    contents = await file.read()
    doc = fitz.open(stream=contents, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

    topics = await run_in_threadpool(extract_topics, api_key, text)

    # generate checklist for each topic concurrently
    import asyncio
    checklists = {}
    async def make_checklist(topic):
        items = await run_in_threadpool(generate_checklist, api_key, topic)
        checklists[topic] = items

    await asyncio.gather(*[make_checklist(t) for t in topics])

    update_notebook(username, notebook_id, {
        "topics": topics,
        "checklists": checklists
    })

    return {"topics": topics, "checklists": checklists}