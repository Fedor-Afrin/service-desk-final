from sqlalchemy.orm import Session
from sqlalchemy import desc
from passlib.context import CryptContext
from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, password_hash=hashed_password, is_admin=user.is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_ticket(db: Session, ticket: schemas.TicketCreate):
    db_ticket = models.Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_tickets(db: Session, user_id: int = None, is_admin: bool = False):
    query = db.query(models.Ticket)
    if not is_admin:
        query = query.filter((models.Ticket.creator_id == user_id) | (models.Ticket.assignee_id == user_id))
    return query.order_by(desc(models.Ticket.created_at)).all()

def get_ticket(db: Session, ticket_id: int):
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

def delete_last_ticket_check(db: Session, ticket_id: int, user_id: int):
    last_ticket = db.query(models.Ticket)\
        .filter(models.Ticket.creator_id == user_id)\
        .order_by(desc(models.Ticket.created_at))\
        .first()
    if last_ticket and last_ticket.id == ticket_id:
        db.delete(last_ticket)
        db.commit()
        return True
    return False

def create_report(db: Session, ticket_id: int, comment: str, file_path: str = None):
    db_report = models.Report(ticket_id=ticket_id, comment=comment, file_path=file_path)
    db.add(db_report)
    db.commit()
    return db_report

def get_reports(db: Session, ticket_id: int):
    return db.query(models.Report).filter(models.Report.ticket_id == ticket_id).all()
