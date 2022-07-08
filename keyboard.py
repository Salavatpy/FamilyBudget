from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from handlers import get_all_categories, get_10_expenses

kb_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить категорию'),
         KeyboardButton(text='Добавить затрату'),

         ],
        [
            KeyboardButton(text='Все категории'),
            KeyboardButton(text='Затраты за месяц'),
            KeyboardButton(text='Затраты за день'),
        ],
        [
            KeyboardButton(text='Удалить категорию'),
            KeyboardButton(text='Удалить затрату'),
        ]
    ],
    resize_keyboard=True
)

kb_exit = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Выход')],
    ],
    resize_keyboard=True
)


def deleting_categories_menu():
    list_of_categories = []
    for i in get_all_categories():
        list_of_categories.append(InlineKeyboardButton(text=i, callback_data=i))
    categories_menu = InlineKeyboardMarkup(row_width=3)
    categories_menu.add(*list_of_categories)
    categories_menu.add(InlineKeyboardButton(text="Выход", callback_data="Выход"))
    return categories_menu


def creating_categories_menu():
    categories_menu = deleting_categories_menu()
    categories_menu.add(InlineKeyboardButton(text="Добавить категорию", callback_data="Добавить категорию"))
    return categories_menu


def creating_expenses_menu():
    list_of_expenses = []
    for i in get_10_expenses():
        list_of_expenses.append(InlineKeyboardButton(text=i, callback_data=i))
    expenses_menu = InlineKeyboardMarkup(row_width=3)
    expenses_menu.add(*list_of_expenses)
    expenses_menu.add(InlineKeyboardButton(text='Выход', callback_data='Выход'))
    return expenses_menu
