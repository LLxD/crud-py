from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
import json

# Connect to the PostgreSQL database

engine = create_engine(
    'sqlite:///airport.db')

# Create a new base class for declarative models
Base = declarative_base()


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    token = Column(String(120), unique=True, nullable=False)

    def __repr__(self):
        return json.dumps(to_dict(self))


class Airport(Base):
    __tablename__ = 'airports'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    origin = Column(String(120), nullable=False)

    def __repr__(self):
        return json.dumps(to_dict(self))


class Flight(Base):
    __tablename__ = 'flights'
    id = Column(Integer, primary_key=True)
    origin = Column(String(80), nullable=False)
    destination = Column(String(120), nullable=False)
    price = Column(String(120), nullable=False)
    max_capacity = Column(Integer, nullable=False)

    def __repr__(self):
        return json.dumps(to_dict(self))


class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(80), nullable=False)
    flight_id = Column(String(120), nullable=False)
    date = Column(String(120), nullable=False)

    def __repr__(self):
        return json.dumps(to_dict(self))


# Create tables
Base.metadata.create_all(engine)
