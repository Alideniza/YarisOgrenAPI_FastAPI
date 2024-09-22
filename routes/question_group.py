from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, School, QuestionGroup, Student
from starlette import status
from sqlalchemy import desc
from .auth import get_current_user

router = APIRouter(
    prefix='/question_groups',
    tags=['Question Group']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class QuestionGroupRequest(BaseModel):
    subject_id: int
    name: str
    is_active: bool
    
@router.get('/get_all_question_groups', status_code=status.HTTP_200_OK)
async def get_all_question_groups(db: db_dependency, user: user_dependency):
    question_groups = db.query(QuestionGroup).filter(QuestionGroup.user_id == user.id).order_by(desc(QuestionGroup.id)).all()
    return question_groups

@router.get('/get_question_group/{question_group_id}', status_code=status.HTTP_200_OK)
async def get_question_group_by_id(db: db_dependency, user: user_dependency, question_group_id: int = Path(gt=0)):
    question_group = db.query(QuestionGroup).filter(QuestionGroup.id == question_group_id, QuestionGroup.user_id == user.id).first()
    if not question_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question Group not found")
    return question_group

@router.post('/create_question_group', status_code=status.HTTP_201_CREATED)
async def create_question_group(db: db_dependency, user: user_dependency, data: QuestionGroupRequest):
    new_question_group = QuestionGroup(**data.dict(), user_id=user.id)
    db.add(new_question_group)
    db.commit()
    db.refresh(new_question_group)
    return new_question_group

@router.put('/update_question_group/{question_group_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_question_group(db: db_dependency, user: user_dependency, data: QuestionGroupRequest, question_group_id: int = Path(gt=0)):
    question_group = db.query(QuestionGroup).filter(QuestionGroup.id == question_group_id, QuestionGroup.user_id == user.id).first()
    if not question_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question Group not found")
    
    question_group.subject_id = data.subject_id
    question_group.name = data.name
    question_group.is_active = data.is_active
    
    db.commit()
    db.refresh(question_group)
    return question_group

@router.delete('/delete_question_group/{question_group_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_group(db: db_dependency, user: user_dependency, question_group_id: int = Path(gt=0)):
    question_group = db.query(QuestionGroup).filter(QuestionGroup.id == question_group_id, QuestionGroup.user_id == user.id).first()
    if not question_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question Group not found")
    
    db.delete(question_group)
    db.commit()
    return {"detail": "Question Group deleted"}