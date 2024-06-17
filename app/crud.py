from sqlalchemy.orm import Session
from datetime import date
from .models import Desk, Booking

def get_desk(db: Session, desk_id: int):
    return db.query(Desk).filter(Desk.id == desk_id).first()

def get_desks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Desk).offset(skip).limit(limit).all()

def create_desk(db: Session, desk: Desk):
    db.add(desk)
    db.commit()
    db.refresh(desk)
    return desk

def update_desk(db: Session, desk_id: int, updated_desk: Desk):
    db_desk = db.query(Desk).filter(Desk.id == desk_id).first()
    if db_desk:
        db_desk.name = updated_desk.name
        db_desk.physical_location = updated_desk.physical_location
        db_desk.virtual_location_x = updated_desk.virtual_location_x
        db_desk.virtual_location_y = updated_desk.virtual_location_y
        db_desk.length = updated_desk.length
        db_desk.width = updated_desk.width
        db.commit()
        db.refresh(db_desk)
    return db_desk

def delete_desk(db: Session, desk_id: int):
    db_desk = db.query(Desk).filter(Desk.id == desk_id).first()
    if db_desk:
        db.delete(db_desk)
        db.commit()
    return db_desk

def book_desk(db: Session, desk_id: int, user: str, booking_date: date):
    new_booking = Booking(desk_id=desk_id, booked_by=user, booked_date=booking_date)
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

def cancel_booking(db: Session, desk_id: int, booking_date: date):
    db_booking = db.query(Booking).filter(Booking.desk_id == desk_id, Booking.booked_date == booking_date).first()
    if db_booking:
        db.delete(db_booking)
        db.commit()
    return db_booking

def get_bookings(db: Session, booking_date: date, skip: int = 0, limit: int = 10):
    return db.query(Booking).filter(Booking.booked_date == booking_date).offset(skip).limit(limit).all()
