import asyncpg
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.default.admin_button import fakultets_menu, tyutors_menu

from loader import dp, db

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    telegram_id = message.from_user.id
    # print(telegram_id)
    db_fios = await db.see_Users(tg_id=telegram_id)
    # print(db_fios)
    with open("zamdekans.txt", "r") as f:
        passwords = [line.strip() for line in f.readlines()]

    if db_fios:
        pass

    else:
        if telegram_id == 5419118871:
            await message.answer("Bot creator Xush kelibsiz", reply_markup=fakultets_menu)
        elif telegram_id == 2051502101:
            await message.answer("Baxtiyor Odilov Xush kelibsiz!", reply_markup=fakultets_menu)
        elif str(telegram_id) in passwords:
            await message.answer("Xush kelibsiz!", reply_markup=fakultets_menu)
        else:
            try:
                user = await db.add_Users(telegram_id=message.from_user.id,
                                           full_name=message.from_user.full_name,
                                           username=message.from_user.username)
                await message.answer(f"Xush kelibsiz, {message.from_user.full_name}!", reply_markup=tyutors_menu)

            except asyncpg.exceptions.UniqueViolationError:
                user = await db.select_Users(telegram_id=message.from_user.id)
