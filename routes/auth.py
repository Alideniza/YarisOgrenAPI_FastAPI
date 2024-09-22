from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from pytest import Session
from sqlalchemy import desc
from models import Role, User, UserRole
from jose import JWTError, jwt
from starlette import status
from database import SessionLocal

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

SECRET_KEY = '8f2fc80b50b09efeba7fef37a806a725e37956e7179563cf28816a77be85b217'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class Token(BaseModel):
    access_token: str
    token_type: str

class UserRequest(BaseModel):
    school_id: int
    lesson_id: int
    email: str
    username: str
    first_name: str
    last_name: str
    phone_number: str
    password: str

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: Annotated[Session, Depends(get_db)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('id')
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate user.")
        
        current_user = db.query(User).filter(User.id == user_id).first()

        if current_user is None:
            raise HTTPException(status_code=401, detail="Could not validate user.")
    
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Session has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return current_user

@router.post("/token", response_model=Token)
async def login_or_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail='Could not validate user.')
    
    token = create_access_token(user.username, user.id, timedelta(minutes=30))
    
    return {'access_token': token, 'token_type': 'bearer'}

@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(db: db_dependency, user: Annotated[dict, Depends(get_current_user)]):
    me = db.query(User).filter(User.id == user.id).first()
    return me

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, data: UserRequest):
    role = db.query(Role).filter(Role.name == "Teacher").first()
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    created_user = User(
        school_id=data.school_id,
        lesson_id=data.lesson_id,
        email=data.email,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
        hashed_password=bcrypt_context.hash(data.password),
        is_active=True
    )
    
    db.add(created_user)
    db.commit()
    db.refresh(created_user)
    
    created_user_role = UserRole(role_id=role.id, user_id=created_user.id)
    db.add(created_user_role)
    
    db.commit()
    
    return created_user

@router.put('/update_user', status_code=status.HTTP_204_NO_CONTENT)
async def update_user(db: db_dependency, user: Annotated[dict, Depends(get_current_user)], data: UserRequest):
    user = db.query(User).filter(User.id == user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.school_id=data.school_id
    user.lesson_id=data.lesson_id
    user.email=data.email
    user.username=data.username
    user.first_name=data.first_name
    user.last_name=data.last_name
    user.phone_number=data.phone_number
    user.hashed_password=bcrypt_context.hash(data.password)
    
    db.commit()
    db.refresh(user)
    return user