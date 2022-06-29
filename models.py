from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    expenses = relationship('Expenses')

    def __init__(self, name):
        self.name = name

    def __str__(self) -> str:
        return f'Категория {self.id}: {self.name}'

    def __repr__(self) -> str:
        return f'Категория {self.id}: {self.name}'


class Expenses(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    category = Column(String, ForeignKey('categories.name'))

    def __init__(self, amount, category):
        self.amount = amount
        self.category = category
