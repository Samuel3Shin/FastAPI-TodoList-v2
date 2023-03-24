import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# # Using sqlite
# DB_URL = "sqlite:///./db.sqlite"
# engine = create_engine(DB_URL, connect_args = { "check_same_thread": False })

# # Using local postgresql
# DB_URL = "postgresql://samuelshin:1234@localhost:5432/postgres"
# engine = create_engine(DB_URL)

# Using posgresql for Docker
DB_URL = os.environ.get("DATABASE_URL", "postgresql://samuelshin:1234@db:5432/postgres")
engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a database session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
