from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    priority = Column(Integer)
    due_date = Column(DateTime)
    owner_id = Column(Integer, index=True)

class TextFile(Base):
    __tablename__ = "textfiles"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    owner_id = Column(Integer, index=True)
