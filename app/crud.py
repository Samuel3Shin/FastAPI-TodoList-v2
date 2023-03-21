from sqlalchemy.orm import Session
from datetime import datetime
from app import models, schemas

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    # hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, current_user_id, skip: int = 0, limit: int = 10):
    db_tasks = db.query(models.Task).filter(models.Task.owner_id == current_user_id).offset(skip).limit(limit).all()
    return db_tasks

def create_task(db: Session, task: schemas.TaskCreate, owner_id: int):
    db_task = models.Task(title=task.title, description=task.description, priority=task.priority, due_date=task.due_date, owner_id=owner_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task: schemas.TaskUpdate):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None
    for attr, value in task.dict(exclude_unset=True).items():
        setattr(db_task, attr, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        return None
    db.delete(db_task)
    db.commit()
    return db_task
