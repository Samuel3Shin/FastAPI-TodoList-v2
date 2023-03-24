from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from app import schemas, crud, auth
from app.database import get_db
from app.auth import oauth2_scheme

router = APIRouter()


@router.get("/tasks", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 10, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)
    tasks = crud.get_tasks(db, current_user.id, skip=skip, limit=limit)
    return tasks


@router.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)
    return crud.create_task(db=db, task=task, owner_id=current_user.id)


@router.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)
    db_task = crud.get_task(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this task")
    return crud.update_task(db=db, task_id=task_id, task=task)


@router.delete("/tasks/{task_id}", response_model=schemas.Task)
def delete_task(task_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)
    db_task = crud.get_task(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete this task")
    return crud.delete_task(db=db, task_id=task_id)
