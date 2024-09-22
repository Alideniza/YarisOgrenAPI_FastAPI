from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, School, Classroom, Student
from starlette import status
from sqlalchemy import desc
from .auth import get_current_user

router = APIRouter(
    prefix='/student',
    tags=['Student']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class StudentRequest(BaseModel):
    classroom_id: int
    name: str
    surname: str
    gender: str
    school_number: int
    is_active: bool

@router.get('/get_all_students', status_code=status.HTTP_200_OK)
async def get_all_students(db: db_dependency, user: user_dependency):
    students = db.query(Student).filter(Student.user_id == user.id).order_by(desc(Student.id)).all()
    return students

@router.get('/get_student/{student_id}', status_code=status.HTTP_200_OK)
async def get_student_by_id(db: db_dependency, user: user_dependency, student_id: int = Path(gt=0)):
    student = db.query(Student).filter(Student.id == student_id, Student.user_id == user.id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student

@router.post('/create_student', status_code=status.HTTP_201_CREATED)
async def create_student(db: db_dependency, user: user_dependency, data: StudentRequest):
    new_student = Student(**data.dict(), user_id=user.id, school_id=user.school_id)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@router.put('/update_student/{student_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_student(db: db_dependency, user: user_dependency, data: StudentRequest, student_id: int = Path(gt=0)):
    student = db.query(Student).filter(Student.id == student_id, Student.user_id == user.id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    
    student.classroom_id = data.classroom_id
    student.name = data.name
    student.surname = data.surname
    student.gender = data.gender
    student.school_number = data.school_number
    student.is_active = data.is_active
    
    db.commit()
    db.refresh(student)
    return student

@router.delete('/delete_student/{student_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(db: db_dependency, user: user_dependency, student_id: int = Path(gt=0)):
    student = db.query(Student).filter(Student.id == student_id, Student.user_id == user.id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    
    db.delete(student)
    db.commit()
    return {"detail": "Student deleted"}

@router.get('/get_student_by_classroom_id/{classroom_id}')
async def get_student_by_classroom_id(db: db_dependency, user: user_dependency, classroom_id: int = Path(gt=0)):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id, Classroom.user_id == user.id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
    
    students = db.query(Student).filter(Student.classroom_id == classroom.id).all()
    return students