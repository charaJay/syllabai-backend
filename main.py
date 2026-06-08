from dotenv import load_dotenv
load_dotenv()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, user, syllabus, chat, notebooks


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://www.syllabai.de",
        "https://syllabai.de",
        "https://syllabai-frontend-production.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, prefix="/user")
app.include_router(notebooks.router, prefix="/notebooks")
app.include_router(syllabus.router, prefix="/syllabus")
app.include_router(chat.router, prefix="/chat")