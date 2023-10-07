import datetime

import asyncpg
import pytz
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.exceptions import TelegramAPIError

from data.config import ADMINS
from keyboards.default.admin_button import fakultets_menu
from loader import dp, db, bot
from states.show_tyutor import Atkif_check, Matematika_check


@dp.message_handler(text="ATKI")
async def atkif_menu(message: types.Message):
    tg_id = message.from_user.id
    faculty = message.text.lower()
    if tg_id == 5419118871:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Atkif_check.next()
    elif tg_id == 5287995033:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Atkif_check.next()
    elif tg_id == 2051502101:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Atkif_check.next()
    else:
        await message.answer(f"<b>Sizga <i>{faculty.upper()}</i> fakultetiga kirish uchun ruhsat mavjud emas.</b>", reply_markup=fakultets_menu)

@dp.message_handler(text=["🛑 To'xtatish"], state=Atkif_check)
async def cancel_atkifTyutor(message: types.Message, state: FSMContext):
    if message.from_user.id == 5419118871:
        await message.answer("Siz <b>ATKI</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    else:
        await message.answer("Siz <b>ATKI</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    await state.reset_state()

@dp.message_handler(state=Atkif_check.tyutor)
async def show_atkif_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("✅ Keldi", "❎ Kelmadi")
    Mk.add("♻️Sababli", "🛑 To'xtatish")
    await message.answer("Davomat holatini kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
    await Atkif_check.next()

@dp.message_handler(lambda message: message.text not in ["✅ Keldi", "❎ Kelmadi", "♻️Sababli"], state=Atkif_check.attendance)
async def davomatdagi_xatolik_atkif(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Atkif_check.attendance)
async def atkif_attendance(message: types.Message, state: FSMContext):
    attendance = message.text
    await state.update_data(
        {"attendance": attendance}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("Tekshirishni davom etish")
    Mk.add("🛑 To'xtatish")
    await message.answer("<b>Bitta tyutorni davomatini tekshirib bo'ldingiz!\nYana davomat tekshirasizmi.</b>\n\n"
                         "yoki 👇 tugmani bosing", reply_markup=Mk)
    await Atkif_check.opportunity.set()

    data = await state.get_data()
    faculty = "atki"
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
    elif nazoratchi == 5287995033:
        tekshirdi += "Maqsudbek Djuraboyev"
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
        atkif = await db.add_davomat(telegram_id=message.from_user.id,
                                               Fullname=data['tyutor'],
                                               Faculty=faculty,
                                               Davomat=data['attendance'],
                                               Vaqti=x,
                                               Tekshirdi=tekshirdi)

        atkif = await db.select_user_davomat(telegram_id=message.from_user.id)
        try:
            show_tyutor = await db.show_Tyutor_name(name=tyutor)
            if show_tyutor:
                for t in show_tyutor:
                    show_tyutorim = t[1].lower()
                    show_tyutorim_tg_id = int(t[2])
                    await bot.send_message(chat_id=show_tyutorim_tg_id, text=mesg)
            await bot.send_message(chat_id=ADMINS[1], text=mesg)
        except TelegramAPIError as e:
            await message.answer(f"<b>Tyutor: {show_tyutorim} bot ma'lumotlar ro'yxatida mavjud emas!</b>")
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)
@dp.message_handler(lambda message: message.text not in ["Tekshirishni davom etish"], state=Atkif_check.opportunity)
async def davomatdagi_imkoniyat_atkif(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Atkif_check.opportunity)
async def atkif_imkoniyat(message: types.Message, state: FSMContext):
    opportunity = message.text.lower()
    await state.update_data(
        {"opportunity": opportunity}
    )
    faculty = "atki"
    if opportunity == 'tekshirishni davom etish':
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Atkif_check.tyutor.set()
    else:
        await message.answer("Shaxsiy sahifangiz.", reply_markup=fakultets_menu)
        #########################tarix#####################
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from states.show_tyutor import Tarix_check

@dp.message_handler(text="TARIX")
async def tarix_menu(message: types.Message):
    tg_id = message.from_user.id
    faculty = message.text.lower()
    if tg_id == 5419118871:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Tarix_check.next()
    elif tg_id == 433569893:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Tarix_check.next()
    elif tg_id == 2051502101:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Tarix_check.next()
    else:
        await message.answer(f"<b>Sizga <i>{faculty.upper()}</i> fakultetiga kirish uchun ruhsat mavjud emas.</b>", reply_markup=fakultets_menu)

@dp.message_handler(text=["🛑 To'xtatish"], state=Tarix_check)
async def cancel_tarixTyutor(message: types.Message, state: FSMContext):
    if message.from_user.id == 5419118871:
        await message.answer("Siz <b>TARIX</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    else:
        await message.answer("Siz <b>TARIX</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    await state.reset_state()

@dp.message_handler(state=Tarix_check.tyutor)
async def show_tarix_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("✅ Keldi", "❎ Kelmadi")
    Mk.add("♻️Sababli", "🛑 To'xtatish")
    await message.answer("Davomat holatini kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
    await Tarix_check.next()

@dp.message_handler(lambda message: message.text not in ["✅ Keldi", "❎ Kelmadi", "♻️Sababli"], state=Tarix_check.attendance)
async def davomatdagi_xatolik_tarix(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Tarix_check.attendance)
async def tarix_attendance(message: types.Message, state: FSMContext):
    attendance = message.text
    await state.update_data(
        {"attendance": attendance}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("Tekshirishni davom etish")
    Mk.add("🛑 To'xtatish")
    await message.answer("<b>Bitta tyutorni davomatini tekshirib bo'ldingiz!\nYana davomat tekshirasizmi.</b>\n\n"
                         "yoki 👇 tugmani bosing", reply_markup=Mk)
    await Tarix_check.opportunity.set()

    data = await state.get_data()
    faculty = "tarix"
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
    elif nazoratchi == 433569893:
        tekshirdi += "Djumabayev Iqboljon"
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
        tarix = await db.add_davomat(telegram_id=message.from_user.id,
                                               Fullname=data['tyutor'],
                                               Faculty=faculty,
                                               Davomat=data['attendance'],
                                               Vaqti=x,
                                               Tekshirdi=tekshirdi)

        tarix = await db.select_user_davomat(telegram_id=message.from_user.id)
        try:
            show_tyutor = await db.show_Tyutor_name(name=tyutor)
            if show_tyutor:
                for t in show_tyutor:
                    show_tyutorim = t[1].lower()
                    show_tyutorim_tg_id = int(t[2])
                    await bot.send_message(chat_id=show_tyutorim_tg_id, text=mesg)
            
            await bot.send_message(chat_id=ADMINS[1], text=mesg)
        except TelegramAPIError as e:
            # print(e)
            await message.answer(f"<b>Tyutor: {show_tyutorim} bot ma'lumotlar ro'yxatida mavjud emas!</b>")
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)
@dp.message_handler(lambda message: message.text not in ["Tekshirishni davom etish"], state=Tarix_check.opportunity)
async def davomatdagi_imkoniyat_tarix(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Tarix_check.opportunity)
async def tarix_imkoniyat(message: types.Message, state: FSMContext):
    opportunity = message.text.lower()
    await state.update_data(
        {"opportunity": opportunity}
    )
    faculty = "tarix"
    if opportunity == 'tekshirishni davom etish':
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Tarix_check.tyutor.set()
    else:
        await message.answer("Shaxsiy sahifangiz.", reply_markup=fakultets_menu)
    ###############tabiiy fanlar#############
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from states.show_tyutor import Tabbiy_fanlar_check

@dp.message_handler(text="TABIIY FANLAR")
async def tabbiy_fanlar_menu(message: types.Message):
    tg_id = message.from_user.id
    faculty = message.text.lower()
    if tg_id == 5419118871:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Tabbiy_fanlar_check.next()
    elif tg_id == 313884048:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Tabbiy_fanlar_check.next()
    elif tg_id == 2051502101:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Tabbiy_fanlar_check.next()
    else:
        await message.answer(f"<b>Sizga <i>{faculty.upper()}</i> fakultetiga kirish uchun ruhsat mavjud emas.</b>", reply_markup=fakultets_menu)

@dp.message_handler(text=["🛑 To'xtatish"], state=Tabbiy_fanlar_check)
async def cancel_tabbiy_fanlarTyutor(message: types.Message, state: FSMContext):
    if message.from_user.id == 5419118871:
        await message.answer("Siz <b>TABIIY FANLAR</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    else:
        await message.answer("Siz <b>TABIIY FANLAR</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    await state.reset_state()

@dp.message_handler(state=Tabbiy_fanlar_check.tyutor)
async def show_tabbiy_fanlar_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("✅ Keldi", "❎ Kelmadi")
    Mk.add("♻️Sababli", "🛑 To'xtatish")
    await message.answer("Davomat holatini kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
    await Tabbiy_fanlar_check.next()

@dp.message_handler(lambda message: message.text not in ["✅ Keldi", "❎ Kelmadi", "♻️Sababli"], state=Tabbiy_fanlar_check.attendance)
async def davomatdagi_xatolik_tabbiy_fanlar(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Tabbiy_fanlar_check.attendance)
async def tabbiy_fanlar_attendance(message: types.Message, state: FSMContext):
    attendance = message.text
    await state.update_data(
        {"attendance": attendance}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("Tekshirishni davom etish")
    Mk.add("🛑 To'xtatish")
    await message.answer("<b>Bitta tyutorni davomatini tekshirib bo'ldingiz!\nYana davomat tekshirasizmi.</b>\n\n"
                         "yoki 👇 tugmani bosing", reply_markup=Mk)
    await Tabbiy_fanlar_check.opportunity.set()

    data = await state.get_data()
    faculty = "tabiiy fanlar"
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
    elif nazoratchi == 313884048:
        tekshirdi += "Tursunov Yahyobek"
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
        tabbiy_fanlar = await db.add_davomat(telegram_id=message.from_user.id,
                                               Fullname=data['tyutor'],
                                               Faculty=faculty,
                                               Davomat=data['attendance'],
                                               Vaqti=x,
                                               Tekshirdi=tekshirdi)

        tabbiy_fanlar = await db.select_user_davomat(telegram_id=message.from_user.id)
        try:
            show_tyutor = await db.show_Tyutor_name(name=tyutor)
            if show_tyutor:
                for t in show_tyutor:
                    show_tyutorim = t[1].lower()
                    show_tyutorim_tg_id = int(t[2])
                    await bot.send_message(chat_id=show_tyutorim_tg_id, text=mesg)
            
            await bot.send_message(chat_id=ADMINS[1], text=mesg)
        except TelegramAPIError as e:
            # print(e)
            await message.answer(f"<b>Tyutor: {show_tyutorim} bot ma'lumotlar ro'yxatida mavjud emas!</b>")
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)
@dp.message_handler(lambda message: message.text not in ["Tekshirishni davom etish"], state=Tabbiy_fanlar_check.opportunity)
async def davomatdagi_imkoniyat_tabbiy_fanlar(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Tabbiy_fanlar_check.opportunity)
async def tabbiy_fanlar_imkoniyat(message: types.Message, state: FSMContext):
    opportunity = message.text.lower()
    await state.update_data(
        {"opportunity": opportunity}
    )
    faculty = "tabiiy fanlar"
    if opportunity == 'tekshirishni davom etish':
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Tabbiy_fanlar_check.tyutor.set()
    else:
        await message.answer("Shaxsiy sahifangiz.", reply_markup=fakultets_menu)
        ###matematika

from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp

@dp.message_handler(text="MATEMATIKA")
async def matematika_menu(message: types.Message):
    tg_id = message.from_user.id
    faculty = message.text.lower()
    if tg_id == 5419118871:# or 591486700 or 2051502101):
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Matematika_check.next()
    elif tg_id == 591486700:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Matematika_check.next()
    elif tg_id == 2051502101:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Matematika_check.next()
    else:
        await message.answer(f"<b>Sizga <i>{faculty.upper()}</i> fakultetiga kirish uchun ruhsat mavjud emas.</b>", reply_markup=fakultets_menu)

@dp.message_handler(text=["🛑 To'xtatish"], state=Matematika_check)
async def cancel_matematikaTyutor(message: types.Message, state: FSMContext):
    if message.from_user.id == 5419118871:
        await message.answer("Siz <b>MATEMATIKA</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    else:
        await message.answer("Siz <b>MATEMATIKA</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    await state.reset_state()

@dp.message_handler(state=Matematika_check.tyutor)
async def show_matematika_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("✅ Keldi", "❎ Kelmadi")
    Mk.add("♻️Sababli", "🛑 To'xtatish")
    await message.answer("Davomat holatini kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
    await Matematika_check.next()

@dp.message_handler(lambda message: message.text not in ["✅ Keldi", "❎ Kelmadi", "♻️Sababli"], state=Matematika_check.attendance)
async def davomatdagi_xatolik_matematika(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Matematika_check.attendance)
async def matematika_attendance(message: types.Message, state: FSMContext):
    attendance = message.text
    await state.update_data(
        {"attendance": attendance}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("Tekshirishni davom etish")
    Mk.add("🛑 To'xtatish")
    await message.answer("<b>Bitta tyutorni davomatini tekshirib bo'ldingiz!\nYana davomat tekshirasizmi.</b>\n\n"
                         "yoki 👇 tugmani bosing", reply_markup=Mk)
    await Matematika_check.opportunity.set()

    data = await state.get_data()
    faculty = "matematika"
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
    elif nazoratchi == 591486700:
        tekshirdi += "Turg'unov Muhammadaziz"
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
        matematika = await db.add_davomat(telegram_id=message.from_user.id,
                                               Fullname=data['tyutor'],
                                               Faculty=faculty,
                                               Davomat=data['attendance'],
                                               Vaqti=x,
                                               Tekshirdi=tekshirdi)

        matematika = await db.select_user_davomat(telegram_id=message.from_user.id)
        try:
            show_tyutor = await db.show_Tyutor_name(name=tyutor)
            if show_tyutor:
                for t in show_tyutor:
                    show_tyutorim = t[1].lower()
                    show_tyutorim_tg_id = int(t[2])
                    await bot.send_message(chat_id=show_tyutorim_tg_id, text=mesg)
            
            await bot.send_message(chat_id=ADMINS[1], text=mesg)
        except TelegramAPIError as e:
            # print(e)
            await message.answer(f"<b>Tyutor: {show_tyutorim} bot ma'lumotlar ro'yxatida mavjud emas!</b>")
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)
@dp.message_handler(lambda message: message.text not in ["Tekshirishni davom etish"], state=Matematika_check.opportunity)
async def davomatdagi_imkoniyat_matematika(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Matematika_check.opportunity)
async def matematika_imkoniyat(message: types.Message, state: FSMContext):
    opportunity = message.text.lower()
    await state.update_data(
        {"opportunity": opportunity}
    )
    faculty = "matematika"
    if opportunity == 'tekshirishni davom etish':
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Matematika_check.tyutor.set()
    else:
        await message.answer("Shaxsiy sahifangiz.", reply_markup=fakultets_menu)
#################fizika################
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from states.show_tyutor import Fizika_check


@dp.message_handler(text="FIZIKA")
async def fizika_menu(message: types.Message):
    tg_id = message.from_user.id
    faculty = message.text.lower()
    if tg_id == 5419118871:  # or 591486700 or 2051502101):
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Fizika_check.next()
    elif tg_id == 591486700:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Fizika_check.next()
    elif tg_id == 2051502101:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Fizika_check.next()
    else:
        await message.answer(f"<b>Sizga <i>{faculty.upper()}</i> fakultetiga kirish uchun ruhsat mavjud emas.</b>",
                             reply_markup=fakultets_menu)
@dp.message_handler(text=["🛑 To'xtatish"], state=Fizika_check)
async def cancel_fizikaTyutor(message: types.Message, state: FSMContext):
    if message.from_user.id == 5419118871:
        await message.answer("Siz <b>FIZIKA</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz",
                             reply_markup=fakultets_menu)
    else:
        await message.answer("Siz <b>FIZIKA</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz",
                             reply_markup=fakultets_menu)
    await state.reset_state()


@dp.message_handler(state=Fizika_check.tyutor)
async def show_fizika_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("✅ Keldi", "❎ Kelmadi")
    Mk.add("♻️Sababli", "🛑 To'xtatish")
    await message.answer("Davomat holatini kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
    await Fizika_check.next()
@dp.message_handler(lambda message: message.text not in ["✅ Keldi", "❎ Kelmadi", "♻️Sababli"],
                    state=Fizika_check.attendance)
async def davomatdagi_xatolik_fizika(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")


@dp.message_handler(state=Fizika_check.attendance)
async def fizika_attendance(message: types.Message, state: FSMContext):
    attendance = message.text
    await state.update_data(
        {"attendance": attendance}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("Tekshirishni davom etish")
    Mk.add("🛑 To'xtatish")
    await message.answer("<b>Bitta tyutorni davomatini tekshirib bo'ldingiz!\nYana davomat tekshirasizmi.</b>\n\n"
                         "yoki 👇 tugmani bosing", reply_markup=Mk)
    await Fizika_check.opportunity.set()

    data = await state.get_data()
    faculty = "fizika"
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
    elif nazoratchi == 591486700:
        tekshirdi += "Karimberdiyev Ulug'bek"
    elif nazoratchi == 50591600:
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
        fizika = await db.add_davomat(telegram_id=message.from_user.id,
                                                 Fullname=data['tyutor'],
                                                 Faculty=faculty,
                                                 Davomat=data['attendance'],
                                                 Vaqti=x,
                                                 Tekshirdi=tekshirdi)

        fizika = await db.select_user_davomat(telegram_id=message.from_user.id)
        try:
            show_tyutor = await db.show_Tyutor_name(name=tyutor)
            if show_tyutor:
                for t in show_tyutor:
                    show_tyutorim = t[1].lower()
                    show_tyutorim_tg_id = int(t[2])
                    await bot.send_message(chat_id=show_tyutorim_tg_id, text=mesg)

            await bot.send_message(chat_id=ADMINS[1], text=mesg)
        except TelegramAPIError as e:
            # print(e)
            await message.answer(f"<b>Tyutor: {show_tyutorim} bot ma'lumotlar ro'yxatida mavjud emas!</b>")
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)
@dp.message_handler(lambda message: message.text not in ["Tekshirishni davom etish"], state=Fizika_check.opportunity)
async def davomatdagi_imkoniyat_fizika(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Fizika_check.opportunity)
async def fizika_imkoniyat(message: types.Message, state: FSMContext):
    opportunity = message.text.lower()
    await state.update_data(
        {"opportunity": opportunity}
    )
    faculty = "fizika"
    if opportunity == 'tekshirishni davom etish':
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Fizika_check.tyutor.set()
    else:
        await message.answer("Shaxsiy sahifangiz.", reply_markup=fakultets_menu)
    #############filologiya##########
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from states.show_tyutor import Filologiya_check

@dp.message_handler(text="FILOLOGIYA")
async def filologiya_menu(message: types.Message):
    tg_id = message.from_user.id
    faculty = message.text.lower()
    if tg_id == 5419118871:# or 564495980 or 2051502101):
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Filologiya_check.next()
    elif tg_id == 564495980:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Filologiya_check.next()
    elif tg_id == 2051502101:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Filologiya_check.next()
    else:
        await message.answer(f"<b>Sizga <i>{faculty.upper()}</i> fakultetiga kirish uchun ruhsat mavjud emas.</b>", reply_markup=fakultets_menu)

@dp.message_handler(text=["🛑 To'xtatish"], state=Filologiya_check)
async def cancel_filologiyaTyutor(message: types.Message, state: FSMContext):
    if message.from_user.id == 5419118871:
        await message.answer("Siz <b>FILOLOGIYA</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    else:
        await message.answer("Siz <b>FILOLOGIYA</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    await state.reset_state()

@dp.message_handler(state=Filologiya_check.tyutor)
async def show_filologiya_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("✅ Keldi", "❎ Kelmadi")
    Mk.add("♻️Sababli", "🛑 To'xtatish")
    await message.answer("Davomat holatini kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
    await Filologiya_check.next()

@dp.message_handler(lambda message: message.text not in ["✅ Keldi", "❎ Kelmadi", "♻️Sababli"], state=Filologiya_check.attendance)
async def davomatdagi_xatolik_filologiya(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Filologiya_check.attendance)
async def filologiya_attendance(message: types.Message, state: FSMContext):
    attendance = message.text
    await state.update_data(
        {"attendance": attendance}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("Tekshirishni davom etish")
    Mk.add("🛑 To'xtatish")
    await message.answer("<b>Bitta tyutorni davomatini tekshirib bo'ldingiz!\nYana davomat tekshirasizmi.</b>\n\n"
                         "yoki 👇 tugmani bosing", reply_markup=Mk)
    await Filologiya_check.opportunity.set()

    data = await state.get_data()
    faculty = "filologiya"
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
    elif nazoratchi == 564495980:
        tekshirdi += "Ergashev Abduhalim"
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
        filologiya = await db.add_davomat(telegram_id=message.from_user.id,
                                               Fullname=data['tyutor'],
                                               Faculty=faculty,
                                               Davomat=data['attendance'],
                                               Vaqti=x,
                                               Tekshirdi=tekshirdi)

        filologiya = await db.select_user_davomat(telegram_id=message.from_user.id)
        try:
            show_tyutor = await db.show_Tyutor_name(name=tyutor)
            if show_tyutor:
                for t in show_tyutor:
                    show_tyutorim = t[1].lower()
                    show_tyutorim_tg_id = int(t[2])
                    await bot.send_message(chat_id=show_tyutorim_tg_id, text=mesg)
            
            await bot.send_message(chat_id=ADMINS[1], text=mesg)
        except TelegramAPIError as e:
            # print(e)
            await message.answer(f"<b>Tyutor: {show_tyutorim} bot ma'lumotlar ro'yxatida mavjud emas!</b>")
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)
@dp.message_handler(lambda message: message.text not in ["Tekshirishni davom etish"], state=Filologiya_check.opportunity)
async def davomatdagi_imkoniyat_filologiya(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Filologiya_check.opportunity)
async def filologiya_imkoniyat(message: types.Message, state: FSMContext):
    opportunity = message.text.lower()
    await state.update_data(
        {"opportunity": opportunity}
    )
    faculty = "filologiya"
    if opportunity == 'tekshirishni davom etish':
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Filologiya_check.tyutor.set()
    else:
        await message.answer("Shaxsiy sahifangiz.", reply_markup=fakultets_menu)
    #############sport##########
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from states.show_tyutor import Jismoniy_madaniyat_check

@dp.message_handler(text="JISMONIY MA'DANIYAT")
async def jismoniy_madaniyat_menu(message: types.Message):
    tg_id = message.from_user.id
    faculty = message.text.lower()
    if tg_id == 5419118871:# or 398900136 or 2051502101):
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Jismoniy_madaniyat_check.next()
    elif tg_id == 398900136:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Jismoniy_madaniyat_check.next()
    elif tg_id == 2051502101:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Jismoniy_madaniyat_check.next()
    else:
        await message.answer(f"<b>Sizga <i>{faculty.upper()}</i> fakultetiga kirish uchun ruhsat mavjud emas.</b>", reply_markup=fakultets_menu)

@dp.message_handler(text=["🛑 To'xtatish"], state=Jismoniy_madaniyat_check)
async def cancel_jismoniy_madaniyatTyutor(message: types.Message, state: FSMContext):
    if message.from_user.id == 5419118871:
        await message.answer("Siz <b>JISMONIY MA'DANIYAT</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    else:
        await message.answer("Siz <b>JISMONIY MA'DANIYAT</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    await state.reset_state()

@dp.message_handler(state=Jismoniy_madaniyat_check.tyutor)
async def show_jismoniy_madaniyat_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("✅ Keldi", "❎ Kelmadi")
    Mk.add("♻️Sababli", "🛑 To'xtatish")
    await message.answer("Davomat holatini kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
    await Jismoniy_madaniyat_check.next()

@dp.message_handler(lambda message: message.text not in ["✅ Keldi", "❎ Kelmadi", "♻️Sababli"], state=Jismoniy_madaniyat_check.attendance)
async def davomatdagi_xatolik_jismoniy_madaniyat(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Jismoniy_madaniyat_check.attendance)
async def jismoniy_madaniyat_attendance(message: types.Message, state: FSMContext):
    attendance = message.text
    await state.update_data(
        {"attendance": attendance}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("Tekshirishni davom etish")
    Mk.add("🛑 To'xtatish")
    await message.answer("<b>Bitta tyutorni davomatini tekshirib bo'ldingiz!\nYana davomat tekshirasizmi.</b>\n\n"
                         "yoki 👇 tugmani bosing", reply_markup=Mk)
    await Jismoniy_madaniyat_check.opportunity.set()

    data = await state.get_data()
    faculty = "jismoniy ma'daniyat"
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
    elif nazoratchi == 398900136:
        tekshirdi += "Mamadaliyev Hayrulloh"
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
        jismoniy_madaniyat = await db.add_davomat(telegram_id=message.from_user.id,
                                               Fullname=data['tyutor'],
                                               Faculty=faculty,
                                               Davomat=data['attendance'],
                                               Vaqti=x,
                                               Tekshirdi=tekshirdi)

        jismoniy_madaniyat = await db.select_user_davomat(telegram_id=message.from_user.id)
        try:
            show_tyutor = await db.show_Tyutor_name(name=tyutor)
            if show_tyutor:
                for t in show_tyutor:
                    show_tyutorim = t[1].lower()
                    show_tyutorim_tg_id = int(t[2])
                    await bot.send_message(chat_id=show_tyutorim_tg_id, text=mesg)
            
            await bot.send_message(chat_id=ADMINS[1], text=mesg)
        except TelegramAPIError as e:
            # print(e)
            await message.answer(f"<b>Tyutor: {show_tyutorim} bot ma'lumotlar ro'yxatida mavjud emas!</b>")
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)
@dp.message_handler(lambda message: message.text not in ["Tekshirishni davom etish"], state=Jismoniy_madaniyat_check.opportunity)
async def davomatdagi_imkoniyat_jismoniy_madaniyat(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Jismoniy_madaniyat_check.opportunity)
async def jismoniy_madaniyat_imkoniyat(message: types.Message, state: FSMContext):
    opportunity = message.text.lower()
    await state.update_data(
        {"opportunity": opportunity}
    )
    faculty = "jismoniy ma'daniyat"
    if opportunity == 'tekshirishni davom etish':
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Jismoniy_madaniyat_check.tyutor.set()
    else:
        await message.answer("Shaxsiy sahifangiz.", reply_markup=fakultets_menu)
###################ijtimoiy##############
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from states.show_tyutor import Ijtimoiy_iqtisodiyot_check

@dp.message_handler(text="IJTIMOIY IQTISODIYOT")
async def ijtimoiy_iqtisodiyot_menu(message: types.Message):
    tg_id = message.from_user.id
    faculty = message.text.lower()
    if tg_id == 5419118871:# or 744216941 or 2051502101):
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Ijtimoiy_iqtisodiyot_check.next()
    elif tg_id == 744216941:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Ijtimoiy_iqtisodiyot_check.next()
    elif tg_id == 2051502101:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Ijtimoiy_iqtisodiyot_check.next()
    else:
        await message.answer(f"<b>Sizga <i>{faculty.upper()}</i> fakultetiga kirish uchun ruhsat mavjud emas.</b>", reply_markup=fakultets_menu)

@dp.message_handler(text=["🛑 To'xtatish"], state=Ijtimoiy_iqtisodiyot_check)
async def cancel_ijtimoiy_iqtisodiyotTyutor(message: types.Message, state: FSMContext):
    if message.from_user.id == 5419118871:
        await message.answer("Siz <b>IJTIMOIY IQTISODIYOT</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    else:
        await message.answer("Siz <b>IJTIMOIY IQTISODIYOT</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    await state.reset_state()

@dp.message_handler(state=Ijtimoiy_iqtisodiyot_check.tyutor)
async def show_ijtimoiy_iqtisodiyot_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("✅ Keldi", "❎ Kelmadi")
    Mk.add("♻️Sababli", "🛑 To'xtatish")
    await message.answer("Davomat holatini kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
    await Ijtimoiy_iqtisodiyot_check.next()

@dp.message_handler(lambda message: message.text not in ["✅ Keldi", "❎ Kelmadi", "♻️Sababli"], state=Ijtimoiy_iqtisodiyot_check.attendance)
async def davomatdagi_xatolik_ijtimoiy_iqtisodiyot(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Ijtimoiy_iqtisodiyot_check.attendance)
async def ijtimoiy_iqtisodiyot_attendance(message: types.Message, state: FSMContext):
    attendance = message.text
    await state.update_data(
        {"attendance": attendance}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("Tekshirishni davom etish")
    Mk.add("🛑 To'xtatish")
    await message.answer("<b>Bitta tyutorni davomatini tekshirib bo'ldingiz!\nYana davomat tekshirasizmi.</b>\n\n"
                         "yoki 👇 tugmani bosing", reply_markup=Mk)
    await Ijtimoiy_iqtisodiyot_check.opportunity.set()

    data = await state.get_data()
    faculty = "ijtimoiy iqtisodiyot"
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
    elif nazoratchi == 744216941:
        tekshirdi += "Ismoilov Sarvarbek"
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
        ijtimoiy_iqtisodiyot = await db.add_davomat(telegram_id=message.from_user.id,
                                               Fullname=data['tyutor'],
                                               Faculty=faculty,
                                               Davomat=data['attendance'],
                                               Vaqti=x,
                                               Tekshirdi=tekshirdi)

        ijtimoiy_iqtisodiyot = await db.select_user_davomat(telegram_id=message.from_user.id)
        try:
            show_tyutor = await db.show_Tyutor_name(name=tyutor)
            if show_tyutor:
                for t in show_tyutor:
                    show_tyutorim = t[1].lower()
                    show_tyutorim_tg_id = int(t[2])
                    await bot.send_message(chat_id=show_tyutorim_tg_id, text=mesg)
            
            await bot.send_message(chat_id=ADMINS[1], text=mesg)
        except TelegramAPIError as e:
            # print(e)
            await message.answer(f"<b>Tyutor: {show_tyutorim} bot ma'lumotlar ro'yxatida mavjud emas!</b>")
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)
@dp.message_handler(lambda message: message.text not in ["Tekshirishni davom etish"], state=Ijtimoiy_iqtisodiyot_check.opportunity)
async def davomatdagi_imkoniyat_ijtimoiy_iqtisodiyot(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=Ijtimoiy_iqtisodiyot_check.opportunity)
async def ijtimoiy_iqtisodiyot_imkoniyat(message: types.Message, state: FSMContext):
    opportunity = message.text.lower()
    await state.update_data(
        {"opportunity": opportunity}
    )
    faculty = "ijtimoiy iqtisodiyot"
    if opportunity == 'tekshirishni davom etish':
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await Ijtimoiy_iqtisodiyot_check.tyutor.set()
    else:
        await message.answer("Shaxsiy sahifangiz.", reply_markup=fakultets_menu)
##############sanatshunoslik
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from states.show_tyutor import San_atshunoslik_check

@dp.message_handler(text="PEDAGOGIKA VA SAN'ATSHUNOSLIK")
async def san_atshunoslik_menu(message: types.Message):
    tg_id = message.from_user.id
    faculty = message.text.lower()
    if tg_id == 5419118871:# or 187805821 or 2051502101):
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await San_atshunoslik_check.next()
    elif tg_id == 187805821:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await San_atshunoslik_check.next()
    elif tg_id == 2051502101:
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await San_atshunoslik_check.next()
    else:
        await message.answer(f"<b>Sizga <i>{faculty.upper()}</i> fakultetiga kirish uchun ruhsat mavjud emas.</b>", reply_markup=fakultets_menu)

@dp.message_handler(text=["🛑 To'xtatish"], state=San_atshunoslik_check)
async def cancel_san_atshunoslikTyutor(message: types.Message, state: FSMContext):
    if message.from_user.id == 5419118871:
        await message.answer("Siz <b>PEDAGOGIKA VA SAN'ATSHUNOSLIK</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    else:
        await message.answer("Siz <b>PEDAGOGIKA VA SAN'ATSHUNOSLIK</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
    await state.reset_state()

@dp.message_handler(state=San_atshunoslik_check.tyutor)
async def show_san_atshunoslik_tyutor(message: types.Message, state: FSMContext):
    tyutor = message.text.lower()
    await state.update_data(
        {"tyutor": tyutor}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("✅ Keldi", "❎ Kelmadi")
    Mk.add("♻️Sababli", "🛑 To'xtatish")
    await message.answer("Davomat holatini kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
    await San_atshunoslik_check.next()

@dp.message_handler(lambda message: message.text not in ["✅ Keldi", "❎ Kelmadi", "♻️Sababli"], state=San_atshunoslik_check.attendance)
async def davomatdagi_xatolik_san_atshunoslik(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
async def san_atshunoslik_attendance(message: types.Message, state: FSMContext):
    attendance = message.text
    await state.update_data(
        {"attendance": attendance}
    )
    Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    Mk.add("Tekshirishni davom etish")
    Mk.add("🛑 To'xtatish")
    await message.answer("<b>Bitta tyutorni davomatini tekshirib bo'ldingiz!\nYana davomat tekshirasizmi.</b>\n\n"
                         "yoki 👇 tugmani bosing", reply_markup=Mk)
    await San_atshunoslik_check.opportunity.set()

    data = await state.get_data()
    faculty = "pedagogika va san'atshunoslik"
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
    elif nazoratchi == 187805821:
        tekshirdi += "san_atshunoslik zamdekani"
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
        san_atshunoslik = await db.add_davomat(telegram_id=message.from_user.id,
                                               Fullname=data['tyutor'],
                                               Faculty=faculty,
                                               Davomat=data['attendance'],
                                               Vaqti=x,
                                               Tekshirdi=tekshirdi)

        san_atshunoslik = await db.select_user_davomat(telegram_id=message.from_user.id)
        try:
            show_tyutor = await db.show_Tyutor_name(name=tyutor)
            if show_tyutor:
                for t in show_tyutor:
                    show_tyutorim = t[1].lower()
                    show_tyutorim_tg_id = int(t[2])
                    await bot.send_message(chat_id=show_tyutorim_tg_id, text=mesg)
            
            await bot.send_message(chat_id=ADMINS[1], text=mesg)
        except TelegramAPIError as e:
            # print(e)
            await message.answer(f"<b>Tyutor: {show_tyutorim} bot ma'lumotlar ro'yxatida mavjud emas!</b>")
    except asyncpg.exceptions.UniqueViolationError:
        await state.reset_state(with_data=True)
@dp.message_handler(lambda message: message.text not in ["Tekshirishni davom etish"], state=San_atshunoslik_check.opportunity)
async def davomatdagi_imkoniyat_san_atshunoslik(message: types.Message):
    """
    davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
    """
    return await message.answer(
        "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")

@dp.message_handler(state=San_atshunoslik_check.opportunity)
async def san_atshunoslik_imkoniyat(message: types.Message, state: FSMContext):
    opportunity = message.text.lower()
    await state.update_data(
        {"opportunity": opportunity}
    )
    faculty = "pedagogika va san'atshunoslik"
    if opportunity == 'tekshirishni davom etish':
        show_tyutor = await db.show_Tyutor(faculty=faculty)
        Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        if show_tyutor:
            for t in show_tyutor:
                show_tyutorim = t[1].lower()
                Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
        Mk.add("🛑 To'xtatish")
        await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
        await San_atshunoslik_check.tyutor.set()
    else:
        await message.answer("Shaxsiy sahifangiz.", reply_markup=fakultets_menu)

#     #################Pedagogika va Sanʼatshunoslik ##################
# import datetime
# import asyncpg
# import pytz
# from aiogram import types
# from aiogram.dispatcher import FSMContext
# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# from aiogram.utils.exceptions import TelegramAPIError
#
# from data.config import ADMINS
# from keyboards.default.admin_button import fakultets_menu
# from loader import dp, db, bot
# from states.show_tyutor import Pedagogika_check
#
# @dp.message_handler(text="PEDAGOGIKA")
# async def pedagogika_menu(message: types.Message):
#     tg_id = message.from_user.id
#     faculty = message.text.lower()
#     if tg_id == 5419118871:# or 2051502101):
#         show_tyutor = await db.show_Tyutor(faculty=faculty)
#         Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
#         if show_tyutor:
#             for t in show_tyutor:
#                 show_tyutorim = t[1].lower()
#                 Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
#         Mk.add("🛑 To'xtatish")
#         await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
#         await Pedagogika_check.next()
#     elif tg_id == 144317937:
#         show_tyutor = await db.show_Tyutor(faculty=faculty)
#         Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
#         if show_tyutor:
#             for t in show_tyutor:
#                 show_tyutorim = t[1].lower()
#                 Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
#         Mk.add("🛑 To'xtatish")
#         await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
#         await Pedagogika_check.next()
#     elif tg_id == 2051502101:
#         show_tyutor = await db.show_Tyutor(faculty=faculty)
#         Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
#         if show_tyutor:
#             for t in show_tyutor:
#                 show_tyutorim = t[1].lower()
#                 Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
#         Mk.add("🛑 To'xtatish")
#         await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
#         await Pedagogika_check.next()
#     else:
#         await message.answer(f"<b>Sizga <i>{faculty.upper()}</i> fakultetiga kirish uchun ruhsat mavjud emas.</b>", reply_markup=fakultets_menu)
#
# @dp.message_handler(text=["🛑 To'xtatish"], state=Pedagogika_check)
# async def cancel_pedagogikaTyutor(message: types.Message, state: FSMContext):
#     if message.from_user.id == 5419118871:
#         await message.answer("Siz <b>PEDAGOGIKA</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
#     else:
#         await message.answer("Siz <b>PEDAGOGIKA</b> fakulteti tyutorlaridan davomat olishni bekor qildingiz", reply_markup=fakultets_menu)
#     await state.reset_state()
#
# @dp.message_handler(state=Pedagogika_check.tyutor)
# async def show_pedagogika_tyutor(message: types.Message, state: FSMContext):
#     tyutor = message.text.lower()
#     await state.update_data(
#         {"tyutor": tyutor}
#     )
#     Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
#     Mk.add("✅ Keldi", "❎ Kelmadi")
#     Mk.add("♻️Sababli", "🛑 To'xtatish")
#     await message.answer("Davomat holatini kiriting. yoki 👇 tugmani bosing", reply_markup=Mk)
#     await Pedagogika_check.next()
#
# @dp.message_handler(lambda message: message.text not in ["✅ Keldi", "❎ Kelmadi", "♻️Sababli"], state=Pedagogika_check.attendance)
# async def davomatdagi_xatolik_pedagogika(message: types.Message):
#     """
#     davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
#     """
#     return await message.answer(
#         "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")
#
# @dp.message_handler(state=Pedagogika_check.attendance)
# async def pedagogika_attendance(message: types.Message, state: FSMContext):
#     attendance = message.text
#     await state.update_data(
#         {"attendance": attendance}
#     )
#     Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
#     Mk.add("Tekshirishni davom etish")
#     Mk.add("🛑 To'xtatish")
#     await message.answer("<b>Bitta tyutorni davomatini tekshirib bo'ldingiz!\nYana davomat tekshirasizmi.</b>\n\n"
#                          "yoki 👇 tugmani bosing", reply_markup=Mk)
#     await Pedagogika_check.opportunity.set()
#
#     data = await state.get_data()
#     faculty = "pedagogika"
#     tyutor = data.get("tyutor")
#     attendance = data.get("attendance")
#     timezone = pytz.timezone("Asia/Tashkent")
#     today = datetime.datetime.now(timezone)
#     year = today.year
#     month = today.month
#     day = today.day
#     hour = today.hour
#     minut = today.minute
#     nazoratchi = message.from_user.id
#     tekshirdi = ""
#     if nazoratchi == 5419118871:
#         tekshirdi += "Shermatov Axlidin"
#     elif nazoratchi == 144317937:
#         tekshirdi += "Nurmatov Mirzoxid"
#     elif nazoratchi == 2051502101:
#         tekshirdi += "Baxtiyor Odilov"
#     else:
#         tekshirdi += nazoratchi
#     x = f"{year}-{month}-{day},{hour}:{minut}"
#     mesg = f"Fakultet ---- <b>✅ {faculty} </b>\n"
#     mesg += f"Tyutor ---- <b>✅ {tyutor}</b>\n"
#     mesg += f"Davomat holati ---- <b>{attendance}</b>\n"
#     mesg += f"Davomat vaqti ----<b>⏰ {x}</b>\n"
#     mesg += f"Tekshirdi ---- <b>🔰{tekshirdi}</b>"
#     await message.answer(f"Siz davomatini tekshirgan {faculty.upper()} fakulteti tyutorining ma'lumotlari:\n{mesg}")
#     try:
#         pedagogika = await db.add_davomat(telegram_id=message.from_user.id,
#                                                Fullname=data['tyutor'],
#                                                Faculty=faculty,
#                                                Davomat=data['attendance'],
#                                                Vaqti=x,
#                                                Tekshirdi=tekshirdi)
#
#         pedagogika = await db.select_user_davomat(telegram_id=message.from_user.id)
#         try:
#             show_tyutor = await db.show_Tyutor_name(name=tyutor)
#             if show_tyutor:
#                 for t in show_tyutor:
#                     show_tyutorim = t[1].lower()
#                     show_tyutorim_tg_id = int(t[2])
#                     await bot.send_message(chat_id=show_tyutorim_tg_id, text=mesg)
#
#             await bot.send_message(chat_id=ADMINS[1], text=mesg)
#         except TelegramAPIError as e:
#             # print(e)
#             await message.answer(f"<b>Tyutor: {show_tyutorim} bot ma'lumotlar ro'yxatida mavjud emas!</b>")
#     except asyncpg.exceptions.UniqueViolationError:
#         await state.reset_state(with_data=True)
# @dp.message_handler(lambda message: message.text not in ["Tekshirishni davom etish"], state=Pedagogika_check.opportunity)
# async def davomatdagi_imkoniyat_pedagogika(message: types.Message):
#     """
#     davomat kiritilishi kerak va qaysi biri bo'lsa shunisini olinadi
#     """
#     return await message.answer(
#         "Kechirasz, bizda bunday belgilash usuli yo'q! Mavjudlaridan birini tanlang.")
#
# @dp.message_handler(state=Pedagogika_check.opportunity)
# async def pedagogika_imkoniyat(message: types.Message, state: FSMContext):
#     opportunity = message.text.lower()
#     await state.update_data(
#         {"opportunity": opportunity}
#     )
#     faculty = "pedagogika"
#     if opportunity == 'tekshirishni davom etish':
#         show_tyutor = await db.show_Tyutor(faculty=faculty)
#         Mk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
#         if show_tyutor:
#             for t in show_tyutor:
#                 show_tyutorim = t[1].lower()
#                 Mk.insert(KeyboardButton(text=show_tyutorim, resize_keyboard=True))
#         Mk.add("🛑 To'xtatish")
#         await message.answer(f"Kerakli tyutorni  tanlang! yoki 👇 tugmani bosing", reply_markup=Mk)
#         await Pedagogika_check.tyutor.set()
#     else:
#         await message.answer("Shaxsiy sahifangiz.", reply_markup=fakultets_menu)