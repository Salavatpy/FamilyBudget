
import logging

from aiogram.utils.executor import start_webhook

import handlers
from aiogram import Bot, Dispatcher, types
from database import create_db
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from states import States
from aiogram.dispatcher import FSMContext
from keyboard import kb_menu, creating_categories_menu, kb_exit, creating_expenses_menu, deleting_categories_menu
import os

TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer("Бот для учёта финансов\n\n", reply_markup=kb_menu)


@dp.message_handler(text=['Все категории'])
async def categories_list(message: types.Message):
    """Отправляет список категорий расходов"""
    if handlers.get_all_categories():
        categories = handlers.get_all_categories()
        answer_message = "Категории трат:\n\n* " + "\n* ".join(categories)
        await message.answer(answer_message, reply_markup=kb_menu)
    else:
        await message.answer("Нет категорий", reply_markup=kb_menu)


@dp.message_handler(text=['Удалить категорию'])
async def delete_category(message: types.Message):
    if handlers.get_all_categories():
        answer_message = "Выберите категорию, которую хотите удалить"
        await message.answer(answer_message, reply_markup=deleting_categories_menu())
        await States.delete_category.set()
    else:
        await message.answer("Нет категорий", reply_markup=kb_menu)


@dp.callback_query_handler(lambda call: True, state=States.delete_category)
async def delete_category_back(callback_query: types.CallbackQuery, state: FSMContext):
    if str(callback_query.data) == "Выход":
        await bot.send_message(callback_query.from_user.id, "Выход в гланое меню",
                               reply_markup=kb_menu)
        await state.finish()
    else:
        handlers.delete_categorie(str(callback_query.data))
        await bot.send_message(callback_query.from_user.id, f'Удалена категория {callback_query.data} !',
                               reply_markup=kb_menu)
        await state.finish()


@dp.message_handler(text=['Удалить затрату'])
async def delete_expense(message: types.Message):
    if handlers.get_10_expenses():
        answer_message = "Выберите затрату, которую хотите удалить"
        await message.answer(answer_message, reply_markup=creating_expenses_menu())
        await States.delete_expense.set()
    else:
        await message.answer("Нет затрат", reply_markup=kb_menu)


@dp.callback_query_handler(lambda call: True, state=States.delete_expense)
async def delete_expense_back(callback_query: types.CallbackQuery, state: FSMContext):
    if str(callback_query.data) == "Выход":
        await bot.send_message(callback_query.from_user.id, "Выход в гланое меню",
                               reply_markup=kb_menu)
        await state.finish()
    else:
        expense_id = (str(callback_query.data).split())[0]
        handlers.delete_expense(expense_id)
        await bot.send_message(callback_query.from_user.id, f'Удалена затрата {callback_query.data} !',
                               reply_markup=kb_menu)
        await state.finish()


@dp.message_handler(text=['Затраты за месяц'])
async def expenses_list(message: types.Message):
    """Отправляет список затрат за месяц"""
    expenses = handlers.get_month_expenses()
    summary = handlers.get_month_expenses_summary()
    if not expenses:
        await message.answer('В этом месяце еще нет затрат', reply_markup=kb_menu)
    else:
        answer_message = "Затраты за текущий месяц:\n\n* " + "\n* ".join(expenses) + f"\n* Итого {summary} тенге"
        await message.answer(answer_message, reply_markup=kb_menu)


@dp.message_handler(text=['Затраты за день'])
async def today_expenses_list(message: types.Message):
    """Отправляет список затрат за день"""
    expenses = handlers.get_today_expenses()
    summary = handlers.get_today_expenses_summary()
    if not expenses:
        await message.answer('Сегодня еще нет затрат', reply_markup=kb_menu)
    else:
        answer_message = "Затраты за текущий день:\n\n* " + "\n* ".join(expenses) + f"\n* Итого {summary} тенге"
        await message.answer(answer_message, reply_markup=kb_menu)


@dp.message_handler(text=['Добавить затрату'])
async def add_expenses(message: types.Message):
    """Добавляет затрату"""
    if handlers.get_all_categories():
        await message.answer('Добавь новую затрату \n Введи ее сумму', reply_markup=kb_exit)
        await States.add_expenses.set()
    else:
        await message.answer('Сначала добавьте категории', reply_markup=kb_menu)


@dp.message_handler(text=['Выход'], state=[States.add_expenses, States.add_category])
async def quit_the_expenses(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Выход в главное меню', reply_markup=kb_menu)


@dp.message_handler(state=States.add_expenses)
async def add_expenses_2(message: types.Message, state: FSMContext):
    if message.text.isnumeric():
        data = float(message.text)
        await state.update_data(add_expenses=data)
        await message.answer('Выбери категорию', reply_markup=creating_categories_menu())
        await States.choose_category.set()
    else:
        await message.answer('Введите число')


@dp.callback_query_handler(lambda call: True, state=States.choose_category)
async def choose_category(callback_query: types.CallbackQuery, state: FSMContext):
    if str(callback_query.data) == "Добавить категорию":
        await bot.send_message(callback_query.from_user.id, text='Добавь новую категорию, \n Введи ее название')
        await States.add_category.set()
    elif str(callback_query.data) == "Выход":
        await bot.send_message(callback_query.from_user.id, "Выход в гланое меню",
                               reply_markup=kb_menu)
        await state.finish()
    else:
        amount = await state.get_data('add_expenses')
        handlers.add_new_expenses(amount['add_expenses'], str(callback_query.data))
        await bot.send_message(callback_query.from_user.id, f'Создана новая затрата! {callback_query.data}',
                               reply_markup=kb_menu)
        await state.finish()


@dp.message_handler(text=['Добавить категорию'])
async def add_category(message: types.Message):
    """Добавляет категорию"""
    await message.answer('Добавь новую категорию, \n Введи ее название', reply_markup=kb_exit)
    await States.add_category.set()


@dp.message_handler(state=States.add_category)
async def add_category_2(message: types.Message, state: FSMContext):
    check_category = handlers.check_categories(message)
    if not check_category:
        answer_message = "Такая категория уже есть\n\n* "
        await message.answer(answer_message)
    else:
        handlers.add_new_category(message.text)
        answer_message = "Создана новая категория\n\n* "
        await message.answer(answer_message, reply_markup=kb_menu)
        await state.finish()


if __name__ == '__main__':
    create_db()
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
