from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from app import schemas, crud, auth
from app.database import get_db

router = APIRouter()

@router.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    user.password = auth.get_password_hash(user.password)
    return crud.create_user(db=db, user=user)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: auth.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/tasks", response_model=List[schemas.Task])
def read_tasks(token, db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)
    tasks = crud.get_tasks(db, current_user.id)
    return tasks

@router.post("/tasks", response_model=schemas.Task)
def create_task(token, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)    
    return crud.create_task(db=db, task=task, owner_id=current_user.id)

@router.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(token, task_id: int, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)    
    db_task = crud.get_task(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this task")
    return crud.update_task(db=db, task_id=task_id, task=task)

@router.delete("/tasks/{task_id}", response_model=schemas.Task)
def delete_task(token, task_id: int, db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)   
    db_task = crud.get_task(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if db_task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this task")
    return crud.delete_task(db=db, task_id=task_id)
