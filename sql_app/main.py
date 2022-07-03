from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/trade/",response_model=schemas.Trade)
def create_trade(trade: schemas.Trade, db: Session = Depends(get_db)):
    return crud.create_trade(db=db, trade=trade)

@app.get("/trade/",response_model=List[schemas.Trade])
def get_trade(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_trade(db=db, skip=skip, limit=limit)

@app.post("/trade_details/",response_model=schemas.TradeDetails)
def create_trade_details(trade_details: schemas.TradeDetails, db: Session = Depends(get_db)):
    return crud.create_trade_details(db=db, trade_details=trade_details)

@app.get("/trade_details/",response_model=List[schemas.TradeDetails])
def get_trade_details(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_trade_details(db=db, skip=skip, limit=limit)
