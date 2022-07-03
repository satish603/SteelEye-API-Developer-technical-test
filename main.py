from typing import Optional, List

from fastapi import Depends, FastAPI, HTTPException,Request,Response
from sqlalchemy.orm import Session
import schemas, models # noqa: E402

from database import SessionLocal,engine



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/trades")
async def get_trades(db: Session = Depends(get_db), limit: Optional[int] = None):
    return db.query(models.Trade).limit(limit).all()


@app.post("/trade")
async def create_trade(trades: schemas.Trade, db: Session = Depends(get_db)):
    new_trade = models.Trade(trade_id=trades.trade_id, trader=trades.trader, asset_class=trades.asset_class,
                             counterparty=trades.counterparty, trade_date_time=trades.trade_date_time,
                             instrument_id=trades.instrument_id, instrument_name=trades.instrument_name)
    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)

    return new_trade
