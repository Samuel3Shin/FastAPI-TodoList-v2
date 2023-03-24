from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app import crud, auth
from app.auth import get_current_user
from app.database import get_db
from app.auth import oauth2_scheme

router = APIRouter()

@router.post("/upload")
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
