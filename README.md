# SteelEye-API-Developer-technical-test
[![N|Solid](https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png)](https://fastapi.tiangolo.com/)
***
##### Given to write the API in Python using the FastAPI framework.
***
### File structure
For these examples, let's say you have a directory named my_super_project that contains a sub-directory called sql_app with a structure like this:

- └── SteelEye-API-Developer-technical-test
    -    ├── _init_.py
    -    ├── crud.py
    -    ├── database.py
    -    ├── main.py
    -    ├── models.py
    -    └── schemas.py

The file _init_.py is just an empty file, but it tells Python that sql_app with all its modules (Python files) is a package.
***
### Schema model
I have been provided a Pydantic model representing a single Trade below:
***
```PYTHON
import datetime as dt
from typing import Optional
from pydantic import BaseModel, Field
class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")
    price: float = Field(description="The price of the Trade.")
    quantity: int = Field(description="The amount of units traded.")
class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None, description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")
    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with. May not always be available")
    instrument_id: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")
    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument traded.")
    trade_date_time: dt.datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")
    trade_details: TradeDetails = Field(alias="tradeDetails", description="The details of the trade, i.e. price, quantity")
    trade_id: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")
    trader: str = Field(description="The name of the Trader")
```
***
### Test to be performed 
In this tests I have build a common request when building an API. where I have provided a set of endpoints for retrieving a list of Trades, retrieving a single Trade by ID, searching against Trades, and filtering Trades.
***
### Create the SQLAlchemy parts
##### Let's refer to the file **./database.py.**
- Import the SQLAlchemy parts
- Create a database URL for SQLAlchemy
- Create a database URL for SQLAlchemy
- Create the SQLAlchemy engine
- Create a SessionLocal class
```PYTHON
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = 'sqlite:///./steeleye.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()
```
***
### Create the database models
##### Let's now see the file **./models.py.**

- Create SQLAlchemy models from the Base class¶
We will use this Base class we created before to create the SQLAlchemy models.
- Import Base from database (the file database.py from above).
 Create classes that inherit from it.
 These classes are the SQLAlchemy models.
- Create model attributes/columns¶
  - Now create all the model (class) attributes.
  - Each of these attributes represents a column in its corresponding database table.
  - We use Column from SQLAlchemy as the default value.
  - And we pass a SQLAlchemy class "type", as Integer, String, and Boolean, that defines the type in the database, as an argument.
- Create the relationships¶
  - Now create the relationships.
  - For this, we use relationship provided by SQLAlchemy ORM.
  - This will become, more or less, a "magic" attribute that will contain the values from other tables related to this one.
```PYTHON
from sqlalchemy import Column, Integer, ForeignKey ,String, Float, Boolean,DateTime 
from sqlalchemy.orm import relationship

from database import Base


class TradeDetails(Base):
    __tablename__ = "trade_details"

    id = Column(String, primary_key=True, index=True)
    buySellIndicator = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    trades = relationship("Trade", back_populates='trade_details')


class Trade(Base):
    __tablename__ = "trade"

    asset_class = Column(String)
    counterparty = Column(String)
    instrument_id = Column(Integer)
    instrument_name = Column(String)
    trade_date_time = Column(DateTime)
    trade_details_id = Column(String, ForeignKey("trade_details.id"))
    trade_details = relationship("TradeDetails", back_populates='trades')
    trade_id = Column(String, primary_key=True, index=True)
    trader = Column(String)
```

***
### Create initial Pydantic models / schemas
```PYTHON
import datetime as dt
from typing import Optional , List
from pydantic import BaseModel, Field
class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")
    price: float = Field(description="The price of the Trade.")
    quantity: int = Field(description="The amount of units traded.")
class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None, description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")
    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with. May not always be available")
    instrument_id: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")
    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument traded.")
    trade_date_time: dt.datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")
    trade_details: List[TradeDetails] = Field(alias="tradeDetails", description="The details of the trade, i.e. price, quantity")
    trade_id: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")
    trader: str = Field(description="The name of the Trader")
```
***
### CRUD utils
- Now let's see the file **./crud.py.**
- In this file we will have reusable functions to interact with the data in the database.
- CRUD comes from: Create, Read, Update, and Delete.
```PYTHON
from sqlalchemy.orm import Session

from import models, schemas


def get_trade_by_id(db: Session, trade_id: str):
    return db.query(models.Trade).filter(models.Trade.trade_id == trade_id).first()

def get_trade(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Trade).offset(skip).limit(limit).all()

def create_trade(db: Session, trade: schemas.Trade):
    db_trade = models.Trade(
        asset_class=trade.asset_class,
        counterparty=trade.counterparty,
        instrument_id=trade.instrument_id,
        instrument_name=trade.instrument_name,
        trade_date_time=trade.trade_date_time,
        trade_id=trade.trade_id,
        trader=trade.trader
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

def get_trade(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Trade).offset(skip).limit(limit).all()

def create_trade_details(db: Session, trade_details: schemas.TradeDetails,trade_id: str):
    
    db_trade_details = models.TradeDetails(
        id=trade_details.id,
        buySellIndicator=trade_details.buySellIndicator,
        price=trade_details.price,
        quantity=trade_details.quantity,
    )
    db.add(db_trade_details)
    db.commit()
    db.refresh(db_trade_details)
    return db_trade_details
```
***
### Main FastAPI app
- And now in the file **./main.py** let's integrate and use all the other parts we created         before. Create the database tables
```PYTHON
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
        
# rest of the code is omitted please check main.py in respo
```
***
### Listing trades
***
![image](https://user-images.githubusercontent.com/60779510/177054853-08634ca9-9805-4427-a07c-3ad49eb7a076.png)
![image](https://user-images.githubusercontent.com/60779510/177054863-3e42daeb-340d-4e61-ac79-f71cc699d03d.png)
![image](https://user-images.githubusercontent.com/60779510/177054887-5519124a-71ed-4cb1-a0a5-eeef6842da72.png)
![image](https://user-images.githubusercontent.com/60779510/177054895-bd0a9c13-57a2-4f5a-913b-075bbcd56de3.png)

***
### Single trade
![image](https://user-images.githubusercontent.com/60779510/177054908-9a6225bd-48f2-4b77-aa5c-68a2ba13363f.png)

***
### Searching trades
***
+ counterparty
    + ![image](https://user-images.githubusercontent.com/60779510/177054925-b7463bc8-ff3b-4aa9-bb18-5fb87f2a9a45.png)

+ InstrumentId
    + ![image](https://user-images.githubusercontent.com/60779510/177054936-3fa01d01-7cb8-457e-9fb1-d4bceef0823c.png)
+ InstrumentName
    + ![image](https://user-images.githubusercontent.com/60779510/177054946-fd7d16dc-ca2e-4d55-b688-ae569a80e8d3.png)
+ Trader
    + ![image](https://user-images.githubusercontent.com/60779510/177054965-d42bfce5-01b7-4497-9c1e-fab2d2249757.png)

### Advanced filtering
The users would able to ability to filter trades with endpoint for fetching a list of trades will need to support filtering using the following optional query parameters:

- ![image](https://user-images.githubusercontent.com/60779510/177075000-e95796e3-a7d7-415d-b123-6bd63b14ffe8.png)
- ![image](https://user-images.githubusercontent.com/60779510/177075021-d790be09-76f5-42f4-b36d-13a1dabe2577.png)


