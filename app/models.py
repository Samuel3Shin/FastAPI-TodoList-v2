from sqlalchemy import Boolean, Column, Integer, String, DateTime, LargeBinary, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    company_name = Column(String)
    credits = Column(Integer)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    priority = Column(Integer)
    due_date = Column(DateTime)
    owner_id = Column(Integer,  ForeignKey("users.id"))


class TextFile(Base):
    __tablename__ = "textfiles"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    owner_id = Column(Integer,  ForeignKey("users.id"))


class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(LargeBinary)
    filename = Column(String, index=True)
    agent_channel = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="audio_files")


User.audio_files = relationship(
    "AudioFile", back_populates="owner", cascade="all, delete, delete-orphan")
