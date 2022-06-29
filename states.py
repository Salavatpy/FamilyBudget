from aiogram.dispatcher.filters.state import StatesGroup, State


class States(StatesGroup):
    add_category = State()
    delete_category = State()
    add_expenses = State()
    choose_category = State()