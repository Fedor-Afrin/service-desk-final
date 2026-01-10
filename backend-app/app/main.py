from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.routers import auth, tickets
from app import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Service Desk API")

app.include_router(auth.router)
app.include_router(tickets.router)

@app.on_event("startup")
def create_default_admin():
    db = SessionLocal()
    if not crud.get_user_by_username(db, "admin"):
        admin_user = schemas.UserCreate(username="admin", password="adminpassword", is_admin=True)
        crud.create_user(db, admin_user)
        print("--- ADMIN USER CREATED: admin / adminpassword ---")
    db.close()
