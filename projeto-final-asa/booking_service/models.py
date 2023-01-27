from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
import json

# Connect to the PostgreSQL database
engine = create_engine('postgresql+psycopg2://postgres:1234@localhost:5432/booking_db')

# Create a new base class for declarative models
Base = declarative_base()

def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

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