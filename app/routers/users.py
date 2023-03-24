from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import schemas, crud, auth
from app.database import get_db
from app.auth import oauth2_scheme

router = APIRouter()


@router.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already registered")
    user.password = auth.get_password_hash(user.password)
    return crud.create_user(db=db, user=user)


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: auth.OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid username or password")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    user.password = auth.get_password_hash(user.password)
    return crud.create_user(db=db, user=user)


@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db_user = crud.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    current_user = auth.get_current_user(token, db)
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db_user = crud.delete_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
