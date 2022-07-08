from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from handlers import get_all_categories

kb_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добваить категорию'),
         KeyboardButton(text='Добавить затрату')
         ],
        [
            KeyboardButton(text='Все категории'),
            KeyboardButton(text='Затраты за месяц'),
            KeyboardButton(text='Затраты за день'),
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


def creating_categories_menu():
    list_of_categories = []
    categories_menu = InlineKeyboardMarkup(row_width=3)
    for i in get_all_categories():
        list_of_categories.append(InlineKeyboardButton(text=i, callback_data=i))
        categories_menu.add(*list_of_categories)
    return categories_menu
