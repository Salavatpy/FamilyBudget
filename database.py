from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

database_url = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)

Base = declarative_base()


def create_db():
    Base.metadata.create_all(engine)
