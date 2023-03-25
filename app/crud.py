from sqlalchemy.orm import Session
from datetime import datetime
from app import models, schemas


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password,
                          company_name=user.company_name, credits=user.credits, is_admin=user.is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    for key, value in user.dict().items():
        if value is not None:
            setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user


def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(db: Session, current_user_id, skip: int = 0, limit: int = 10):
    db_tasks = db.query(models.Task).filter(
        models.Task.owner_id == current_user_id).offset(skip).limit(limit).all()
    return db_tasks


def create_task(db: Session, task: schemas.TaskCreate, owner_id: int):
    db_task = models.Task(title=task.title, description=task.description,
                          priority=task.priority, due_date=task.due_date, owner_id=owner_id)
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


def save_text_file_content(db: Session, content: str, owner_id: int):
    text_file = models.TextFile(content=content, owner_id=owner_id)
    db.add(text_file)
    db.commit()
    pass


def save_audio_file(db: Session, content: bytes, filename: str, agent_channel: str, owner_id: int):
    audio_file = models.AudioFile(
        content=content, filename=filename, agent_channel=agent_channel, owner_id=owner_id)
    db.add(audio_file)
    db.commit()
    db.refresh(audio_file)
    return audio_file


def get_audio_file_by_id(db: Session, audio_id: int):
    return db.query(models.AudioFile).filter(models.AudioFile.id == audio_id).first()


def get_audio_files_by_owner(db: Session, owner_id: int):
    return db.query(models.AudioFile).filter(models.AudioFile.owner_id == owner_id).all()


def get_all_audio_files(db: Session):
    return db.query(models.AudioFile).all()
