import datetime
import logging

import asyncpg
import pytz
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.exceptions import TelegramAPIError

from data.config import ADMINS
from keyboards.default.admin_button import fakultets_menu
from loader import dp, db, bot
from states.show_tyutor import Pedagogika_check

@dp.message_handler(text="PEDAGOGIKA")
async def pedagogika_menu(message: types.Message):
    tg_id = message.from_user.id
    faculty = message.text.lower()
    if tg_id == (5419118871 or 2051502101):
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Pedagogika_check.next()
    else:
        await message.answer(f"<b>Sizga <i>{faculty.upper()}</i> fakultetiga kirish uchun ruhsat mavjud emas.</b>", reply_markup=fakultets_menu)

@dp.message_handler(text=["🛑 To'xtatish"], state=Pedagogika_check)
async def cancel_pedagogikaTyutor(message: types.Message, state: FSMContext):
    if message.from_user.id == 5419118871:
        await message.answer("Siz <b>PEDAGOGIKA</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    else:
        await message.answer("Siz <b>PEDAGOGIKA</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    await state.reset_state()

@dp.message_handler(state=Pedagogika_check.tyutor)
async def show_pedagogika_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("✅ Keldi", "❎ Kelmadi")
    Mk.add("♻️Sababli", "🛑 To'xtatish")
    await message.answer("Davomat holatini kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
    await Pedagogika_check.next()

@dp.message_handler(lambda message: message.text not in ["✅ Keldi", "❎ Kelmadi", "♻️Sababli"], state=Pedagogika_check.attendance)
async def davomatdagi_xatolik_pedagogika(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Pedagogika_check.attendance)
async def pedagogika_attendance(message: types.Message, state: FSMContext):
    attendance = message.text
    await state.update_data(
        {"attendance": attendance}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("Xa", "Yo'q")
    Mk.add("🛑 To'xtatish")
    await message.answer("<b>Bitta tyutorni davomatini tekshirib bo'ldingiz!\nYana davomat tekshirasizmi.</b>\n\n"
                         "yoki 👇 tugmani bosing", reply_markup=Mk)
    await Pedagogika_check.opportunity.set()

    data = await state.get_data()
    faculty = "pedagogika"
    tyutor = data.get("tyutor")
    attendance = data.get("attendance")
    timezone = pytz.timezone("Asia/Tashkent")
    today = datetime.datetime.now(timezone)
    year = today.year
    month = today.month
    day = today.day
    hour = today.hour
    minut = today.minute
    nazoratchi = message.from_user.id
    tekshirdi = ""
    if nazoratchi == 5419118871:
        tekshirdi += "Shermatov Axlidin"
    # elif nazoratchi == 187805821:
    #     tekshirdi += "pedagogika zamdekani"
    elif nazoratchi == 2051502101:
        tekshirdi += "Baxtiyor Odilov"
    else:
        tekshirdi += nazoratchi
    x = f"{year}-{month}-{day},{hour}:{minut}"
    mesg = f"Fakultet ---- <b>✅ {faculty} </b>\n"
    mesg += f"Tyutor ---- <b>✅ {tyutor}</b>\n"
    mesg += f"Davomat holati ---- <b>{attendance}</b>\n"
    mesg += f"Davomat vaqti ----<b>⏰ {x}</b>\n"
    mesg += f"Tekshirdi ---- <b>🔰{tekshirdi}</b>"
    await message.answer(f"Siz davomatini tekshirgan {faculty.upper()} fakulteti tyutorining ma'lumotlari:\n{mesg}")
    try:
        pedagogika = await db.add_davomat(telegram_id=message.from_user.id,
                                               Fullname=data['tyutor'],
                                               Faculty=faculty,
                                               Davomat=data['attendance'],
                                               Vaqti=x,
                                               Tekshirdi=tekshirdi)

        pedagogika = await db.select_user_davomat(telegram_id=message.from_user.id)
        try:
            show_tyutor = await db.show_Tyutor_name(name=tyutor)
            if show_tyutor:
                for t in show_tyutor:
                    show_tyutorim = t[1].lower()
                    show_tyutorim_tg_id = t[2]
                    # await bot.send_message(chat_id=show_tyutorim_tg_id, text=mesg)
            await bot.send_message(chat_id=ADMINS[0], text=mesg)
            # await bot.send_message(chat_id=ADMINS[1], text=mesg)
        except TelegramAPIError as e:
            # print(e)
            await message.answer(f"<b>Tyutor: {show_tyutorim} bot ma'lumotlar ro'yxatida mavjud emas!</b>")
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)
@dp.message_handler(lambda message: message.text not in ["Xa", "Yo'q"], state=Pedagogika_check.opportunity)
async def davomatdagi_imkoniyat_pedagogika(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Pedagogika_check.opportunity)
async def pedagogika_imkoniyat(message: types.Message, state: FSMContext):
    opportunity = message.text.lower()
    await state.update_data(
        {"opportunity": opportunity}
    )
    faculty = "pedagogika"
    if opportunity == 'xa':
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Pedagogika_check.tyutor.set()
    else:
        await message.answer("Shaxsiy sahifangiz.", reply_markup=fakultets_menu)