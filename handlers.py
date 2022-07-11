from models import Categories, Expenses
from database import Session
from datetime import datetime, timedelta


def get_all_categories():
    session = Session()
    result = []
    for i in session.query(Categories).all():
        result.append(i.name)
    return list(result)


def get_10_expenses():
    session = Session()
    result = []
    for i in session.query(Expenses).limit(10):
        category = session.query(Categories).filter(Categories.id == i.category).first()
        result.append(f'{i.id} {category.name} сумма {i.amount} тенге')
    return list(result)


def get_month_expenses():
    session = Session()
    result = []
    summary = 0
    filter_after = datetime.today() - timedelta(days=30)
    for i in session.query(Expenses).filter(Expenses.created_date >= filter_after).all():
        category = session.query(Categories).filter(Categories.id == i.category).first()
        expense = f'Категория {category.name}, затрата {i.amount} тенге, дата {i.created_date.date()}'
        result.append(expense)
        summary += i.amount
    return list(result)


def get_month_expenses_summary():
    session = Session()
    summary = 0
    filter_after = datetime.today() - timedelta(days=30)
    for i in session.query(Expenses).filter(Expenses.created_date >= filter_after).all():
        summary += i.amount
    return summary


def get_today_expenses():
    session = Session()
    result = []
    summary = 0
    filter_after = datetime.today() - timedelta(days=1)
    for i in session.query(Expenses).filter(Expenses.created_date >= filter_after).all():
        category = session.query(Categories).filter(Categories.id == i.category).first()
        expense = f'Категория {category.name}, затрата {i.amount} тенге, время {i.created_date.time().strftime("%H:%M")}'
        result.append(expense)
        summary += i.amount
    return list(result)


def get_today_expenses_summary():
    session = Session()
    summary = 0
    filter_after = datetime.today() - timedelta(days=1)
    for i in session.query(Expenses).filter(Expenses.created_date >= filter_after).all():
        summary += i.amount
    return summary


def check_categories(message):
    session = Session()
    category = session.query(Categories).filter(Categories.name == message.text).first()
    if category is None:
        return True
    else:
        return False


def add_new_category(message):
    session = Session()
    category = Categories(name=message)
    session.add(category)
    session.commit()
    session.close()


def add_new_expenses(amount, category):
    session = Session()
    category = session.query(Categories).filter(Categories.name == category).first()
    expense = Expenses(amount=amount, category=category.id)
    session.add(expense)
    session.commit()
    session.close()


def delete_categorie(category):
    session = Session()
    category = session.query(Categories).filter(Categories.name == category).first()
    session.delete(category)
    session.commit()
    session.close()


def delete_expense(expense_id):
    session = Session()
    expense = session.query(Expenses).filter(Expenses.id == expense_id).first()
    session.delete(expense)
    session.commit()
    session.close()