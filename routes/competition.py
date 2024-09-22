from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import QuestionGroup, Student, User, School, Classroom, Competition
from starlette import status
from sqlalchemy import desc
from .auth import get_current_user

router = APIRouter(
    prefix='/competition',
    tags=['Competition']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class CompetitionRequest(BaseModel):
    classroom_id: int
    question_group_id: int
    name: str
    competition_key: str
    competition_point: int
    is_active: bool
    
@router.get('/get_all_competitions', status_code=status.HTTP_200_OK)
async def get_all_competitions(db: db_dependency, user: user_dependency):
    competitions = db.query(Competition).filter(Competition.user_id == user.id).order_by(desc(Competition.id)).all()
    return competitions

@router.get('/get_competition/{competition_id}', status_code=status.HTTP_200_OK)
async def get_competition_by_id(db: db_dependency, user: user_dependency, competition_id: int = Path(gt=0)):
    competition = db.query(Competition).filter(Competition.id == competition_id, Competition.user_id == user.id).first()
    if not competition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competition not found")
    return competition

@router.post('/create_competition', status_code=status.HTTP_201_CREATED)
async def create_competition(db: db_dependency, user: user_dependency, data: CompetitionRequest):
    new_competition = Competition(**data.dict(), user_id=user.id)
    db.add(new_competition)
    db.commit()
    db.refresh(new_competition)
    return new_competition

@router.put('/update_competition/{competition_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_competition(db: db_dependency, user: user_dependency, data: CompetitionRequest, competition_id: int = Path(gt=0)):
    competition = db.query(Competition).filter(Competition.id == competition_id, Competition.user_id == user.id).first()
    if not competition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competition not found")
    
    competition.classroom_id = data.classroom_id
    competition.question_group_id = data.question_group_id
    competition.name = data.name
    competition.competition_key = data.competition_key
    competition.competition_point = data.competition_point
    competition.is_active = data.is_active
    
    db.commit()
    db.refresh(competition)
    return competition

@router.delete('/delete_competition/{competition_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_competition(db: db_dependency, user: user_dependency, competition_id: int = Path(gt=0)):
    competition = db.query(Competition).filter(Competition.id == competition_id, Competition.user_id == user.id).first()
    if not competition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competition not found")
    
    db.delete(competition)
    db.commit()
    return {"detail": "Competition deleted"}

@router.get('/get_competition_by_classroom_id/{classroom_id}')
async def get_competition_by_classroom_id(db: db_dependency, user: user_dependency, classroom_id: int = Path(gt=0)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id, Classroom.user_id == user.id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
    
    competitions = db.query(Competition).filter(Competition.classroom_id == classroom.id).all()
    return competitions

@router.get('/get_competition_by_question_group_id/{question_group_id}')
async def get_competition_by_competition_group_id(db: db_dependency, user: user_dependency, question_group_id: int = Path(gt=0)):
    question_group = db.query(QuestionGroup).filter(QuestionGroup.id == question_group_id, QuestionGroup.user_id == user.id).first()
    if not question_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competition Group not found")
    
    competitions = db.query(Competition).filter(Competition.question_group_id == question_group.id).all()
    return competitions