from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime,Float
from sqlalchemy.orm import relationship

from .database import Base


class Trade(Base):
    __tablename__ = "trade"

    id = Column(Integer, primary_key=True, index=True)
    asset_class=Column(String,default=None)
    counterparty=Column(String,default=None)
    instrument_id=Column(String)
    instrument_name=Column(String)
    trade_date_time=Column(DateTime)
    trade_details=relationship("TradeDetails",back_populates="owner")
    trade_id=Column(String,unique=True,default=None)
    trader=Column(String)
    


    

class TradeDetails(Base):
    __tablename__ = "trade_details"

    id = Column(Integer, primary_key=True, index=True)
    trade_id=Column(String,primary_key=True)
    buySellIndicator=Column(String)
    price=Column(Float)
    quantity=Column(Integer)
    owner_id=Column(String,ForeignKey("trade.trade_id")) 
    owner=relationship("Trade",back_populates="trade_details")


