import datetime
from typing import Any

import pytz
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship
from database import Base


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    expenses = relationship('Expenses')

    def __init__(self, name, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.name = name

    def __str__(self) -> str:
        return f'Категория {self.id}: {self.name}'

    def __repr__(self) -> str:
        return f'Категория {self.id}: {self.name}'


class Expenses(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    created_date = Column(DateTime(timezone=True), default=datetime.now(pytz.timezone('Asia/Almaty')))
    category = Column(Integer, ForeignKey('categories.id'), default=None)

    def __init__(self, amount, category, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.amount = amount
        self.category = category
