from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = "sqlite:///./db.sqlite"

engine = create_engine(DB_URL, connect_args = { "check_same_thread": False })
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a database session
def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()