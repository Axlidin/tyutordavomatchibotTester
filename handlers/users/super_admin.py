import datetime

import asyncpg
import pytz
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from data import config
from keyboards.default.admin_button import super_admin_meu, fakultets_menu
from loader import dp, db
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from states.show_tyutor import Add_database, Delete_database, Update_database


@dp.message_handler(chat_id=5419118871, text="from_excel_to_db")
async def to_db_from_excel(message: types.Message):
    tg_id = message.from_user.id
    if tg_id == 5419118871:
        excel_file_path = 'data/malumotlar.xlsx'
        df = pd.read_excel(excel_file_path)

        # PostgreSQL ma'lumotlar bazasi bog'lanishi
        db_params = {
            'dbname': f'{config.DB_NAME}',
            'user': f'{config.DB_USER}',
            'password': f"{config.DB_PASS}",
            'host': f"{config.DB_HOST}",  # Ma'lumotlar bazasi serverining manzili
            'port': f"{config.DB_PORT}"  # PostgreSQL sukutiy porti
        }

        connection = psycopg2.connect(**db_params)
        cursor = connection.cursor()

        # Ma'lumotlarni PostgreSQLga yozish
        engine = create_engine(
            f'postgresql://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["dbname"]}')
        df.to_sql('tyutor', engine, if_exists='replace', index=False)

        # Bog'lanishlarni yopish
        cursor.close()
        connection.close()
        await message.answer("Ma'lumotlar bazasiga excel fayl yuklandi.")
################to db add va delete########
@dp.message_handler(chat_id=5419118871, text="super_admin")
async def super_adminMenu(message: types.Message):
    await message.answer("Kerakli bo'limni tanlang.", reply_markup=super_admin_meu)

@dp.message_handler(chat_id=5419118871, text="Delete_db")
async def super_admin_del_Menu(message: types.Message):
    await message.answer("Kerakli fakultetni tanlang.", reply_markup=fakultets_menu)
    await Delete_database.next()

@dp.message_handler(state=Delete_database.faculty)
async def showFaculty_menu(message: types.Message, state: FSMContext):
    faculty = message.text.lower()
    await state.update_data(
        {"faculty": faculty}
    )
    show_tyutor = await db.show_Tyutor(faculty=faculty)
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    if show_tyutor:
        for t in show_tyutor:
            show_tyutorim = t[1].lower()
            Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Delete_database.next()
####"🏠"
@dp.message_handler(text=["🏠"])
async def mainMenu(message: types.Message):
    await message.answer("Asosiy sahifa", reply_markup=fakultets_menu)

@dp.message_handler(text=["🛑 To'xtatish"], state=Delete_database)
async def cancel_add_baza(message: types.Message, state: FSMContext):
    await message.answer("Siz <b>tyutor o'chirishni</b> bekor qildingiz", reply_markup=super_admin_meu)
    await state.reset_state()

@dp.message_handler(state=Delete_database.tyutor)
async def my_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    data = await state.get_data()
    faculty = data.get("faculty")
    delete_tyutor = await db.delete_db_tyutor(del_name=tyutor)
    if not delete_tyutor:
        await message.answer("Hozirda bunday ismli tyutor yo'q.", reply_markup=super_admin_meu)
    else:
        await message.answer(f"<b>Siz <i>{faculty.upper()}</i> fakultetitdan <i>{tyutor.upper()}</i>ni  o'chirdingiz</b>", reply_markup=super_admin_meu)
        await state.reset_state(with_data=True)
############add databse#############
@dp.message_handler(chat_id=5419118871, text="Add_db")
async def super_admin_add_Menu(message: types.Message):
    await message.answer("Kerakli fakultetni tanlang.", reply_markup=fakultets_menu)
    await Add_database.next()

@dp.message_handler(state=Add_database.faculty)
async def showadd_faculty_menu(message: types.Message, state: FSMContext):
    faculty = message.text.lower()
    await state.update_data(
        {"faculty": faculty}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("🛑 To'xtatish")
    await message.answer(f"Kerakli tyutorni ismi familiyasini to'liq kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
    await Add_database.next()

@dp.message_handler(text=["🛑 To'xtatish"], state=Add_database)
async def cancel_add_baza(message: types.Message, state: FSMContext):
    await message.answer("Siz <b>tyutor qo'shishni</b> bekor qildingiz", reply_markup=super_admin_meu)
    await state.reset_state()

@dp.message_handler(state=Add_database.tyutor)
async def my_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    await message.answer(f"{tyutor.upper()} ning telegram id raqamini kiriting.")
    await Add_database.next()

@dp.message_handler(state=Add_database.telegram_id)
async def my_tyutor_tg_id(message: types.Message, state: FSMContext):
    telegram_id = message.text
    await state.update_data(
        {"telegram_id": telegram_id}
    )
    data = await state.get_data()
    faculty = data.get('faculty')
    tyutor = data.get("tyutor")
    telegram_id = data.get("telegram_id")
    timezone = pytz.timezone("Asia/Tashkent")
    today = datetime.datetime.now(timezone)
    year = today.year
    month = today.month
    day = today.day
    hour = today.hour
    minut = today.minute
    x = f"{year}-{month}-{day},{hour}:{minut}"
    mesg = f"Fakultet ---- <b>✅ {faculty} </b>\n"
    mesg += f"Tyutor ---- <b>✅ {tyutor}</b>\n"
    mesg += f"Telegram id ---- <b>✅{telegram_id}</b>\n"
    mesg += f"Tyutor qo'shilgan vaqt ----<b>⏰ {x}</b>\n"
    mesg += f"Super admin ---- <b>🔰Shermatov Axlidin</b>"
    await message.answer(f"{faculty.upper()} fakulteti tyutorining ma'lumotlari:\n{mesg}", reply_markup=super_admin_meu)
    await state.finish()
    try:
        add_database = await db.add_tyutor(telegram_id=int(telegram_id),
                                               fullname=tyutor,
                                               faculty=faculty)

        add_database = await db.select_user_tyutor(telegram_id=int(telegram_id))
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)

        ############update db######
from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db
@dp.message_handler(text="update_telegram_id")
async def update_tg_id(message: types.Message):
    await message.answer("Kerakli fakultetni tanlang.", reply_markup=fakultets_menu)
    await Update_database.next()

@dp.message_handler(state=Update_database.faculty)
async def showaupdate_faculty_menu(message: types.Message, state: FSMContext):
    faculty = message.text.lower()
    await state.update_data(
        {"faculty": faculty}
    )
    show_tyutor = await db.show_Tyutor(faculty=faculty)
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    if show_tyutor:
        for t in show_tyutor:
            show_tyutorim = t[1].lower()
            Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Update_database.next()

@dp.message_handler(text=["🛑 To'xtatish"], state=Update_database)
async def cancel_add_baza(message: types.Message, state: FSMContext):
    await message.answer("Siz <b>Telegram id </b>yangilashni bekor qildingiz", reply_markup=super_admin_meu)
    await state.reset_state()

@dp.message_handler(state=Update_database.tyutor)
async def update_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    await message.answer(f"{tyutor.upper()} ning yangi telegram id raqamini kiriting.")
    await Update_database.next()

@dp.message_handler(state=Update_database.telegram_id)
async def update_tg_id(message: types.Message, state: FSMContext):
    telegram_id = message.text
    await state.update_data(
        {"telegram_id": telegram_id}
    )
    data = await state.get_data()
    faculty = data.get('faculty')
    tyutor = data.get("tyutor")
    telegram_id = data.get("telegram_id")
    timezone = pytz.timezone("Asia/Tashkent")
    today = datetime.datetime.now(timezone)
    year = today.year
    month = today.month
    day = today.day
    hour = today.hour
    minut = today.minute
    x = f"{year}-{month}-{day},{hour}:{minut}"
    mesg = f"Fakultet ---- <b>✅ {faculty} </b>\n"
    mesg += f"Tyutor ---- <b>✅ {tyutor}</b>\n"
    mesg += f"Yangi telegram id ---- <b>✅{telegram_id}</b>\n"
    mesg += f"Super admin ---- <b>🔰Shermatov Axlidin</b>"

    await state.finish()
    try:
        await db.update_user_username_tyutor(telegram_id=int(telegram_id),
                                           fullname=tyutor)
        await message.answer(f"Yangilandi: \n{mesg}",
                             reply_markup=super_admin_meu)
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)
