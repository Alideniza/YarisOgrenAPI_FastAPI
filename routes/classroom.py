from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, School, Classroom
from starlette import status
from sqlalchemy import desc
from .auth import get_current_user

router = APIRouter(
    prefix='/classroom',
    tags=['Classroom']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class ClassroomRequest(BaseModel):
    name: str
    classroom_number: int
    is_active: bool

@router.get('/get_all_classrooms', status_code=status.HTTP_200_OK)
async def get_all_classrooms(db: db_dependency, user: user_dependency):
    classrooms = db.query(Classroom).filter(Classroom.user_id == user.id).order_by(desc(Classroom.id)).all()
    return classrooms

@router.get('/get_classroom/{classroom_id}', status_code=status.HTTP_200_OK)
async def get_classroom_by_id(db: db_dependency, user: user_dependency, classroom_id: int = Path(gt=0)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id, Classroom.user_id == user.id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
    return classroom

@router.post('/create_classroom', status_code=status.HTTP_201_CREATED)
async def create_classroom(db: db_dependency, user: user_dependency, data: ClassroomRequest):
    new_classroom = Classroom(**data.dict(), user_id=user.id, school_id=user.school_id)
    db.add(new_classroom)
    db.commit()
    db.refresh(new_classroom)
    return new_classroom

@router.put('/update_classroom/{classroom_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_classroom(db: db_dependency, user: user_dependency, data: ClassroomRequest, classroom_id: int = Path(gt=0)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id, Classroom.user_id == user.id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
    
    classroom.name = data.name
    classroom.classroom_number = data.classroom_number
    classroom.is_active = data.is_active
    
    db.commit()
    db.refresh(classroom)
    return classroom

@router.delete('/delete_classroom/{classroom_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_classroom(db: db_dependency, user: user_dependency, classroom_id: int = Path(gt=0)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id, Classroom.user_id == user.id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
    
    db.delete(classroom)
    db.commit()
    return {"detail": "Classroom deleted"}