from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import QuestionGroup, User, School, Classroom, Question
from starlette import status
from sqlalchemy import desc
from .auth import get_current_user

router = APIRouter(
    prefix='/question',
    tags=['Question']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class QuestionRequest(BaseModel):
    question_group_id: int
    name: str
    question_text: str
    correct_answer: str
    answer_1: str
    answer_2: str
    answer_3: str
    answer_4: str
    answer_5: str
    is_active: bool
    
@router.get('/get_all_questions', status_code=status.HTTP_200_OK)
async def get_all_questions(db: db_dependency, user: user_dependency):
    questions = db.query(Question).filter(Question.user_id == user.id).order_by(desc(Question.id)).all()
    return questions

@router.get('/get_question/{question_id}', status_code=status.HTTP_200_OK)
async def get_question_by_id(db: db_dependency, user: user_dependency, question_id: int = Path(gt=0)):
    question = db.query(Question).filter(Question.id == question_id, Question.user_id == user.id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return question

@router.post('/create_question', status_code=status.HTTP_201_CREATED)
async def create_question(db: db_dependency, user: user_dependency, data: QuestionRequest):
    new_question = Question(**data.dict(), user_id=user.id)
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@router.put('/update_question/{question_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_question(db: db_dependency, user: user_dependency, data: QuestionRequest, question_id: int = Path(gt=0)):
    question = db.query(Question).filter(Question.id == question_id, Question.user_id == user.id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    
    question.question_group_id = data.question_group_id
    question.name = data.name
    question.question_text = data.question_text
    question.correct_answer = data.correct_answer
    question.answer_1 = data.answer_1
    question.answer_2 = data.answer_2
    question.answer_3 = data.answer_3
    question.answer_4 = data.answer_4
    question.answer_5 = data.answer_5
    question.is_active = data.is_active
    
    db.commit()
    db.refresh(question)
    return question

@router.delete('/delete_question/{question_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(db: db_dependency, user: user_dependency, question_id: int = Path(gt=0)):
    question = db.query(Question).filter(Question.id == question_id, Question.user_id == user.id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    
    db.delete(question)
    db.commit()
    return {"detail": "Question deleted"}

@router.get('/get_question_by_question_group_id/{question_group_id}')
async def get_question_by_question_group_id(db: db_dependency, user: user_dependency, question_group_id: int = Path(gt=0)):
    question_group = db.query(QuestionGroup).filter(QuestionGroup.id == question_group_id, QuestionGroup.user_id == user.id).first()
    if not question_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question Group not found")
    
    questions = db.query(Question).filter(Question.question_group_id == question_group.id).all()
    return questions