from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/tickets", tags=["tickets"])
MEDIA_DIR = "/app/media"

@router.post("/", response_model=schemas.TicketResponse)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    return crud.create_ticket(db, ticket)

@router.get("/", response_model=List[schemas.TicketResponse])
def read_tickets(user_id: int, is_admin: bool = False, db: Session = Depends(get_db)):
    return crud.get_tickets(db, user_id=user_id, is_admin=is_admin)

@router.get("/{ticket_id}", response_model=schemas.TicketResponse)
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    return crud.get_ticket(db, ticket_id)

@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, user_id: int, db: Session = Depends(get_db)):
    success = crud.delete_last_ticket_check(db, ticket_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="You can only delete your last created ticket")
    return {"status": "deleted"}

@router.post("/{ticket_id}/reports")
def add_report(
    ticket_id: int,
    comment: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    file_path = None
    if file:
        file_path = f"{ticket_id}_{file.filename}"
        full_path = os.path.join(MEDIA_DIR, file_path)
        with open(full_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    crud.create_report(db, ticket_id, comment, file_path)
    return {"status": "ok"}

@router.get("/{ticket_id}/reports", response_model=List[schemas.ReportResponse])
def get_reports(ticket_id: int, db: Session = Depends(get_db)):
    return crud.get_reports(db, ticket_id)
