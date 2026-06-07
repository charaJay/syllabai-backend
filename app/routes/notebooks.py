from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth import get_current_user
from app.users import (
    get_notebooks, get_notebook, create_notebook,
    update_notebook, delete_notebook
)

router = APIRouter()


class ChecklistToggle(BaseModel):
    topic: str
    index: int
    done: bool

class NotebookCreate(BaseModel):
    name: str
    color: str


class NotebookUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


@router.get("/")
def list_notebooks(username: str = Depends(get_current_user)):
    return {"notebooks": get_notebooks(username)}


@router.post("/")
def new_notebook(body: NotebookCreate, username: str = Depends(get_current_user)):
    notebook = create_notebook(username, body.name, body.color)
    return notebook


@router.get("/{notebook_id}")
def fetch_notebook(notebook_id: str, username: str = Depends(get_current_user)):
    notebook = get_notebook(username, notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found.")
    return notebook


@router.patch("/{notebook_id}")
def edit_notebook(notebook_id: str, body: NotebookUpdate, username: str = Depends(get_current_user)):
    updated = update_notebook(username, notebook_id, body.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Notebook not found.")
    return updated


@router.delete("/{notebook_id}")
def remove_notebook(notebook_id: str, username: str = Depends(get_current_user)):
    success = delete_notebook(username, notebook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notebook not found.")
    return {"message": "Notebook deleted."}


@router.patch("/{notebook_id}/checklist")
def toggle_checklist_item(
    notebook_id: str,
    body: ChecklistToggle,
    username: str = Depends(get_current_user)
):
    notebook = get_notebook(username, notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found.")

    checklists = notebook.get("checklists", {})
    topic_list = checklists.get(body.topic, [])

    if body.index >= len(topic_list):
        raise HTTPException(status_code=400, detail="Invalid checklist index.")

    topic_list[body.index]["done"] = body.done
    checklists[body.topic] = topic_list
    update_notebook(username, notebook_id, {"checklists": checklists})
    return {"ok": True}