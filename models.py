from datetime import datetime
from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean

class MyBase():
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=str(datetime.now()))
    updated_at = Column(String, default=str(datetime.now()), onupdate=str(datetime.now()))



# Roles #

class Role(MyBase, Base):
    __tablename__ = "roles"

class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))
    
# Roles #



# Cities, District, School #

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))

class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey('cities.id'))
    name = Column(String(255))

class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey('districts.id'))
    name = Column(String(255))

# Cities, District, School #



# Lesson, Subject #

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    name = Column(String(255))
    
# Lesson, Subject #



# User #
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey('schools.id'))
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    email = Column(String(255), unique=True)
    username = Column(String(50), unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    phone_number = Column(String(50))

# User #



# Other #

class Classroom(MyBase, Base):
    __tablename__ = "classrooms"

    user_id = Column(Integer, ForeignKey('users.id'))
    school_id = Column(Integer, ForeignKey('schools.id'))
    classroom_number = Column(String(10))

class Student(MyBase, Base):
    __tablename__ = "students"

    user_id = Column(Integer, ForeignKey('users.id'))
    school_id = Column(Integer, ForeignKey('schools.id'))
    classroom_id = Column(Integer, ForeignKey('classrooms.id'))
    surname = Column(String(50))
    gender = Column(String(10))
    school_number = Column(Integer)

class QuestionGroup(MyBase, Base):
    __tablename__ = "question_groups"

    user_id = Column(Integer, ForeignKey('users.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))

class Question(MyBase, Base):
    __tablename__ = "questions"

    user_id = Column(Integer, ForeignKey('users.id'))
    question_group_id = Column(Integer, ForeignKey('question_groups.id'))
    question_text = Column(String(500))
    correct_answer = Column(String(50))
    answer_1 = Column(String(50))
    answer_2 = Column(String(50))
    answer_3 = Column(String(50))
    answer_4 = Column(String(50))
    answer_5 = Column(String(50))

class Competition(MyBase, Base):
    __tablename__ = "competitions"

    user_id = Column(Integer, ForeignKey('users.id'))
    classroom_id = Column(Integer, ForeignKey('classrooms.id'))
    question_group_id = Column(Integer, ForeignKey('question_groups.id'))
    competition_key = Column(String(50))
    competition_point = Column(Integer)

class Point(MyBase, Base):
    __tablename__ = "points"

    user_id = Column(Integer, ForeignKey('users.id'))
    student_id = Column(Integer, ForeignKey('students.id'))
    point_value = Column(Integer)
