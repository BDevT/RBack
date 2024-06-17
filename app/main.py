from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
import json
import os

from .models import Base, Desk, SessionLocal, engine
from .crud import get_desk, get_desks, create_desk, update_desk, delete_desk, book_desk, cancel_booking, get_bookings

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Pydantic models
class DeskCreate(BaseModel):
    name: str
    physical_location: str
    virtual_location_x: float = Field(..., ge=0.0, le=1.0)
    virtual_location_y: float = Field(..., ge=0.0, le=1.0)
    length: float = Field(..., ge=0.0, le=1.0)
    width: float = Field(..., ge=0.0, le=1.0)

class DeskUpdate(BaseModel):
    name: Optional[str]
    physical_location: Optional[str]
    virtual_location_x: Optional[float] = Field(None, ge=0.0, le=1.0)
    virtual_location_y: Optional[float] = Field(None, ge=0.0, le=1.0)
    length: Optional[float] = Field(None, ge=0.0, le=1.0)
    width: Optional[float] = Field(None, ge=0.0, le=1.0)

class DeskResponse(BaseModel):
    id: int
    name: str
    physical_location: str
    virtual_location_x: float
    virtual_location_y: float
    length: float
    width: float

    class Config:
        orm_mode = True

class BookingResponse(BaseModel):
    id: int
    desk_id: int
    booked_by: str
    booked_date: date

    class Config:
        orm_mode = True

class DeskBooking(BaseModel):
    user: str
    booking_date: date

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize desks from local JSON file
def init_desks_from_json(db: Session):
    json_file_path = os.path.join(os.path.dirname(__file__), 'initial_desks.json')
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            desks_data = json.load(file)
            for desk_data in desks_data:
                desk_exists = get_desk(db, desk_id=desk_data.get("id"))
                if not desk_exists:
                    desk = Desk(**desk_data)
                    db.add(desk)
            db.commit()

@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        init_desks_from_json(db)
    finally:
        db.close()

@app.get("/desks/", response_model=List[DeskResponse])
def read_desks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    desks = get_desks(db, skip=skip, limit=limit)
    return desks

@app.get("/desks/{desk_id}", response_model=DeskResponse)
def read_desk(desk_id: int, db: Session = Depends(get_db)):
    db_desk = get_desk(db, desk_id=desk_id)
    if db_desk is None:
        raise HTTPException(status_code=404, detail="Desk not found")
    return db_desk

@app.post("/desks/", response_model=DeskResponse)
def create_desk_item(desk: DeskCreate, db: Session = Depends(get_db)):
    db_desk = Desk(**desk.dict())
    return create_desk(db, db_desk)

@app.put("/desks/{desk_id}", response_model=DeskResponse)
def update_desk_item(desk_id: int, desk: DeskUpdate, db: Session = Depends(get_db)):
    db_desk = get_desk(db, desk_id=desk_id)
    if db_desk is None:
        raise HTTPException(status_code=404, detail="Desk not found")
    updated_desk = Desk(**desk.dict(exclude_unset=True))
    return update_desk(db, desk_id, updated_desk)

@app.delete("/desks/{desk_id}", response_model=DeskResponse)
def delete_desk_item(desk_id: int, db: Session = Depends(get_db)):
    db_desk = get_desk(db, desk_id=desk_id)
    if db_desk is None:
        raise HTTPException(status_code=404, detail="Desk not found")
    return delete_desk(db, desk_id)

@app.post("/desks/{desk_id}/book", response_model=BookingResponse)
def book_desk_item(desk_id: int, booking: DeskBooking, db: Session = Depends(get_db)):
    db_desk = get_desk(db, desk_id=desk_id)
    if db_desk is None:
        raise HTTPException(status_code=404, detail="Desk not found")
    return book_desk(db, desk_id, booking.user, booking.booking_date)

@app.post("/desks/{desk_id}/cancel", response_model=BookingResponse)
def cancel_booking_item(desk_id: int, booking_date: date, db: Session = Depends(get_db)):
    db_desk = get_desk(db, desk_id=desk_id)
    if db_desk is None:
        raise HTTPException(status_code=404, detail="Desk not found")
    return cancel_booking(db, desk_id, booking_date)

@app.get("/bookings", response_model=List[BookingResponse])
def read_bookings(booking_date: date = Query(...), skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookings = get_bookings(db, booking_date=booking_date, skip=skip, limit=limit)
    return bookings
