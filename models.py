# models.py
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class TestData(Base):
    __tablename__ = 'testdata'
    id = Column(BigInteger(),primary_key=True,autoincrement=True)
    flightDate = Column(Date, nullable=False)
    flightStatus = Column(String(12))
    departureAirport = Column(String(50))
    departureTimezone = Column(String(50))
    departureTerminal = Column(String(10))
    departureGate = Column(String(10))
    departureDelay = Column(Integer)
    departureScheduled = Column(DateTime(timezone=False))
    departureEstimated = Column(DateTime(timezone=False))
    arrivalAirport = Column(String(50))
    arrivalTimezone = Column(String(50))
    arrivalTerminal = Column(String(10))
    arrivalGate = Column(String(10))
    arrivalBaggage = Column(String(10))
    arrivalDelay = Column(Integer)
    arrivalScheduled = Column(DateTime(timezone=False))
    arrivalEstimated = Column(DateTime(timezone=False))
    airlineName = Column(String(50))
    flightNumber = Column(String(10))
    departureScheduledCordoba = Column(DateTime(timezone=False))
    arrivalScheduledCordoba = Column(DateTime(timezone=False))
    flightDuration = Column(String(20))
    createdAt = Column(DateTime(timezone=False))
