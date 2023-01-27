from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base


import json

# Connect to the PostgreSQL database
engine = create_engine('postgresql+psycopg2://postgres:1234@localhost:5432/user_db')

# Create a new base class for declarative models
Base = declarative_base()


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), unique=True, nullable=False)
    token = Column(String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

# Create tables
Base.metadata.create_all(engine)
