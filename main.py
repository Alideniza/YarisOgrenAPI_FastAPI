from fastapi import APIRouter, FastAPI
from database import engine
from routes import admin, auth, classroom, student, question_group, question, competition
from models import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

api_router = APIRouter()

api_router.include_router(admin.router)
api_router.include_router(auth.router)
api_router.include_router(classroom.router)
api_router.include_router(student.router)
api_router.include_router(question_group.router)
api_router.include_router(question.router)
api_router.include_router(competition.router)

app.include_router(api_router, prefix="/api")