"""Сервер Telegram бота, запускаемый непосредственно"""

import logging

from aiogram.utils.executor import start_webhook

import handlers
from aiogram import Bot, Dispatcher, types
from database import create_db
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from states import States
from aiogram.dispatcher import FSMContext
from keyboard import kb_menu, creating_categories_menu, kb_exit
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


# @dp.message_handler(lambda message: message.text.startswith('/del'))
# async def del_expense(message: types.Message):
#     """Удаляет одну запись о расходе по её идентификатору"""
#     row_id = int(message.text[4:])
#     expenses.delete_expense(row_id)
#     answer_message = "Удалил"
#     await message.answer(answer_message)


@dp.message_handler(text=['Все категории'])
async def categories_list(message: types.Message):
    """Отправляет список категорий расходов"""
    categories = handlers.get_all_categories()
    answer_message = "Категории трат:\n\n* " + "\n* ".join(categories)
    await message.answer(answer_message, reply_markup=kb_menu)


@dp.message_handler(text=['Затраты за месяц'])
async def expenses_list(message: types.Message):
    """Отправляет список категорий расходов"""
    expenses = handlers.get_month_expenses()
    summary = handlers.get_month_expenses_summary()
    if not expenses:
        await message.answer('В этом месяце еще нет затрат', reply_markup=kb_menu)
    else:
        answer_message = "Затраты за текущий месяц:\n\n* " + "\n* ".join(expenses) + f"\n* Итого {summary} тенге"
        await message.answer(answer_message, reply_markup=kb_menu)


@dp.message_handler(text=['Затраты за день'])
async def today_expenses_list(message: types.Message):
    """Отправляет список категорий расходов"""
    expenses = handlers.get_today_expenses()
    summary = handlers.get_today_expenses_summary()
    if not expenses:
        await message.answer('Сегодня еще нет затрат', reply_markup=kb_menu)
    else:
        answer_message = "Затраты за текущий день:\n\n* " + "\n* ".join(expenses) + f"\n* Итого {summary} тенге"
        await message.answer(answer_message, reply_markup=kb_menu)


# @dp.message_handler(lambda message: message.text.startswith('/addcategory'))
# async def add_categorie(message: types.Message):
#     """Добавляет категорию расходов"""
#     add_new_category(message.text[13:])
#     answer_message = "Создана новая категория\n\n* "
#     await message.answer(answer_message)

@dp.message_handler(text=['Добавить затрату'])
async def add_expenses(message: types.Message):
    await message.answer('Добавь новую затрату \n Введи ее сумму', reply_markup=kb_exit)
    await States.add_expenses.set()


@dp.message_handler(text=['Выход'], state=States.add_expenses)
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
    amount = await state.get_data('add_expenses')
    handlers.add_new_expenses(amount['add_expenses'], str(callback_query.data))
    await bot.send_message(callback_query.from_user.id, f'Создана новая затрата! {callback_query.data}',
                           reply_markup=kb_menu)
    await state.finish()


@dp.message_handler(text=['Добваить категорию'])
async def add_category(message: types.Message):
    await message.answer('Добавь новую категорию, \n Введи ее название', reply_markup=kb_exit)
    await States.add_category.set()


@dp.message_handler(text=['Выход'], state=States.add_category)
async def quit_the_expenses(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Выход в главное меню', reply_markup=kb_menu)


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


# @dp.message_handler(commands=['today'])
# async def today_statistics(message: types.Message):
#     """Отправляет сегодняшнюю статистику трат"""
#     answer_message = expenses.get_today_statistics()
#     await message.answer(answer_message)


# @dp.message_handler(commands=['month'])
# async def month_statistics(message: types.Message):
#     """Отправляет статистику трат текущего месяца"""
#     answer_message = expenses.get_month_statistics()
#     await message.answer(answer_message)


# @dp.message_handler(commands=['expenses'])
# async def list_expenses(message: types.Message):
#     """Отправляет последние несколько записей о расходах"""
#     last_expenses = expenses.last()
#     if not last_expenses:
#         await message.answer("Расходы ещё не заведены")
#         return

#     last_expenses_rows = [
#         f"{expense.amount} руб. на {expense.category_name} — нажми "
#         f"/del{expense.id} для удаления"
#         for expense in last_expenses]
#     answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* "\
#             .join(last_expenses_rows)
#     await message.answer(answer_message)


# @dp.message_handler()
# async def add_expense(message: types.Message):
#     """Добавляет новый расход"""
#     try:
#         expense = expenses.add_expense(message.text)
#     except exceptions.NotCorrectMessage as e:
#         await message.answer(str(e))
#         return
#     answer_message = (
#         f"Добавлены траты {expense.amount} руб на {expense.category_name}.\n\n"
#         f"{expenses.get_today_statistics()}")
#     await message.answer(answer_message)


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

