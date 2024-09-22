from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "mssql+pyodbc://yarisogren_db:yarisogren2024+-*@5.180.184.132/YarisOgren_DB?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes&MultipleActiveResultSets=true"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()