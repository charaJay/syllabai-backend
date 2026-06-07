import json
import uuid
from pathlib import Path

USERS_DIR = Path("data/users")
USERS_DIR.mkdir(parents=True, exist_ok=True)


def _user_path(username: str) -> Path:
    return USERS_DIR / f"{username}.json"


def find_user(username: str) -> dict | None:
    path = _user_path(username)
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def create_user(username: str, hashed_password: str) -> dict:
    user = {
        "username": username,
        "password": hashed_password,
        "api_key": None,
        "notebooks": []
    }
    with open(_user_path(username), "w") as f:
        json.dump(user, f, indent=2)
    return user


def update_user(username: str, data: dict) -> dict:
    with open(_user_path(username), "w") as f:
        json.dump(data, f, indent=2)
    return data


def get_notebooks(username: str) -> list:
    user = find_user(username)
    if not user:
        return []
    return user.get("notebooks", [])


def get_notebook(username: str, notebook_id: str) -> dict | None:
    user = find_user(username)
    if not user:
        return None
    return next((n for n in user.get("notebooks", []) if n["id"] == notebook_id), None)


def create_notebook(username: str, name: str, color: str) -> dict:
    user = find_user(username)
    notebook = {
        "id": str(uuid.uuid4()),
        "name": name,
        "color": color,
        "topics": [],
        "conversations": {}
    }
    user.setdefault("notebooks", []).append(notebook)
    update_user(username, user)
    return notebook


def update_notebook(username: str, notebook_id: str, data: dict) -> dict | None:
    user = find_user(username)
    notebooks = user.get("notebooks", [])
    for i, n in enumerate(notebooks):
        if n["id"] == notebook_id:
            notebooks[i] = {**n, **data}
            user["notebooks"] = notebooks
            update_user(username, user)
            return notebooks[i]
    return None


def delete_notebook(username: str, notebook_id: str) -> bool:
    user = find_user(username)
    notebooks = user.get("notebooks", [])
    new_notebooks = [n for n in notebooks if n["id"] != notebook_id]
    if len(new_notebooks) == len(notebooks):
        return False
    user["notebooks"] = new_notebooks
    update_user(username, user)
    return True