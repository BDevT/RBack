from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os


# SQLALCHEMY_DATABASE_URL = "sqlite:///./app/test.db"
SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/test.db"

if os.path.exists("/tmp/test.db"):
    os.remove("/tmp/test.db")
    
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Desk(Base):
    __tablename__ = "desks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    physical_location = Column(String)
    virtual_location_x = Column(Float)
    virtual_location_y = Column(Float)
    length = Column(Float)
    width = Column(Float)

    bookings = relationship("Booking", back_populates="desk")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    desk_id = Column(Integer, ForeignKey('desks.id'))
    booked_by = Column(String, nullable=False)
    booked_date = Column(Date, nullable=False)

    desk = relationship("Desk", back_populates="bookings")

Base.metadata.create_all(bind=engine)
