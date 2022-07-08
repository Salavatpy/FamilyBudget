from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)

Base = declarative_base()


def create_db():
    Base.metadata.create_all(engine)
