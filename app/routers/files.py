from typing import List
from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, HTTPException, File, UploadFile
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
    if not crud.save_text_file_content(db, decoded_content, owner_id=current_user.id):
        raise HTTPException(status_code=400, detail="Insufficient credits.")

    return {"filename": file.filename}


@router.post("/upload_audio")
async def upload_audio_file(
    file: UploadFile = File(...),
    agent_channel: str = Form(...),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type")
    current_user = auth.get_current_user(token, db)
    filename = file.filename
    content = await file.read()

    # Save the content and agent_channel to the database
    audio_file = crud.save_audio_file(db, content=content, filename=filename,
                                      agent_channel=agent_channel, owner_id=current_user.id)
    if not audio_file:
        raise HTTPException(status_code=400, detail="Insufficient credits.")

    return {"filename": file.filename}


@router.delete("/delete_audio/{audio_id}", response_model=schemas.AudioFile)
def delete_audio_file(audio_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = auth.get_current_user(token, db)
    audio_file = crud.delete_audio_file(db, audio_id)
    if not current_user.is_admin and current_user.id != audio_file.owner_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if audio_file is None:
        raise HTTPException(status_code=404, detail="Audio file not found")
    return audio_file


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

    if not current_user.is_admin and audio_file.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this audio file")

    return Response(audio_file.content, media_type="audio/mpeg")


@router.get("/user_audios", response_model=List[schemas.AudioFile])
async def get_user_audio_files(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = auth.get_current_user(token, db)
    if current_user.is_admin:
        audio_files = crud.get_all_audio_files(db)
    else:
        audio_files = crud.get_audio_files_by_owner(
            db, owner_id=current_user.id)
    return audio_files
