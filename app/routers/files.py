from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app import crud, auth
from app.auth import get_current_user
from app.database import get_db
from app.auth import oauth2_scheme

router = APIRouter()

@router.post("/upload_text")
async def upload_text_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    current_user = auth.get_current_user(token, db)
    content = await file.read()
    decoded_content = content.decode("utf-8")

    # Save the content to the database
    crud.save_text_file_content(db, decoded_content, owner_id=current_user.id)

    return {"filename": file.filename}

@router.post("/upload_audio")
async def upload_audio_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    current_user = auth.get_current_user(token, db)
    filename = file.filename
    content = await file.read()

    # Save the content to the database
    crud.save_audio_file(db, content=content, filename=filename, owner_id=current_user.id)

    return {"filename": file.filename}