from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from .database import SessionLocal, engine, Base
from . import models, can_handler

# Ensure the tables are created
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/messages")
def read_messages(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    messages = db.query(models.CANMessage).offset(skip).limit(limit).all()
    return messages

@app.post("/messages")
def create_message(db: Session = Depends(get_db)):
    message = can_handler.read_can_message()
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

@app.get("/db-check")
def read_root(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        return {"status": "Database is connected", "result": result[0]}
    except Exception as e:
        return {"status": "Database is not connected", "error": str(e)}
