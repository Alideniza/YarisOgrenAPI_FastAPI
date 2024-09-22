from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from pytest import Session
from sqlalchemy import desc
from models import Classroom, Competition, Point, Question, QuestionGroup, Role, Student, User, UserRole
from starlette import status
from database import SessionLocal
from routes.auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/users", status_code=status.HTTP_200_OK)
async def get_all_user(db: db_dependency, user: user_dependency):
    user_roles = (
        db.query(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user.id)
        .all()
    )
    
    if not any(role.name == 'Admin' for role in user_roles):
        raise HTTPException(status_code=403, detail="Unauthorized to access this endpoint")
        
    users = db.query(User).order_by(desc(User.id)).all()
    return users

@router.delete('/delete_user/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user: user_dependency, user_id: int = Path(gt=0)):
    user_roles = (
        db.query(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user.id)
        .all()
    )
    
    if not any(role.name == 'Admin' for role in user_roles):
        raise HTTPException(status_code=403, detail="Unauthorized to access this endpoint")
    
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    points_to_delete = db.query(Point).filter(Point.user_id == user_id).all()
    for point in points_to_delete:
        db.delete(point)
        db.commit()
        
    competitions_to_delete = db.query(Competition).filter(Competition.user_id == user_id).all()
    for competition in competitions_to_delete:
        db.delete(competition)
        db.commit()
        
    questions_to_delete = db.query(Question).filter(Question.user_id == user_id).all()
    for question in questions_to_delete:
        db.delete(question)
        db.commit()
        
    question_groups_to_delete = db.query(QuestionGroup).filter(QuestionGroup.user_id == user_id).all()
    for question_group in question_groups_to_delete:
        db.delete(question_group)
        db.commit()
        
    students_to_delete = db.query(Student).filter(Student.user_id == user_id).all()
    for student in students_to_delete:
        db.delete(student)
        db.commit()
    
    classrooms_to_delete = db.query(Classroom).filter(Classroom.user_id == user_id).all()
    for classroom in classrooms_to_delete:
        db.delete(classroom)
        db.commit()
        
    user_roles_to_delete = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    for user_role in user_roles_to_delete:
        db.delete(user_role)
        db.commit()
        
    db.delete(user_to_delete)
    db.commit()

