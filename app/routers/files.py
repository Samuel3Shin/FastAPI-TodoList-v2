from typing import List
from fastapi import APIRouter, Depends, File, Response, UploadFile, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app import crud, auth, schemas
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
    crud.save_audio_file(db, content=content,
                         filename=filename, owner_id=current_user.id)

    return {"filename": file.filename}


@router.get("/audio/{audio_id}", response_model=bytes, responses={
    200: {
        "content": {
            "audio/mpeg": {}
        }
    }
})
async def get_audio_file(audio_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = auth.get_current_user(token, db)
    audio_file = crud.get_audio_file_by_id(db, audio_id)

    if audio_file is None:
        raise HTTPException(status_code=404, detail="Audio file not found")

    if audio_file.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this audio file")

    return Response(audio_file.content, media_type="audio/mpeg")


@router.get("/user_audios", response_model=List[schemas.AudioFile])
async def get_user_audio_files(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = auth.get_current_user(token, db)
    audio_files = crud.get_audio_files_by_owner(db, owner_id=current_user.id)
    return audio_files
