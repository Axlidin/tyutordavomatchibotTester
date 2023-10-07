import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardRemove

from keyboards.default.admin_button import fakultets_menu, tyutors_menu
from keyboards.inline.support import support_keyboard, support_callback
from loader import dp, bot
from aiogram.dispatcher.filters import Text

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler2(message: types.Message, state: FSMContext):
    """
    Foydalanuvchiga har qanday harakatni bekor qilishga ruxsat bering
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    with open("zamdekans.txt", "r") as f:
        passwords = [line.strip() for line in f.readlines()]

    if message.from_user.id == 2051502101:
        await message.answer("Sizning xabaringiz Bekor qilndi.!", reply_markup=fakultets_menu)
    elif message.from_user.id in passwords:
        await message.answer("Sizning xabaringiz Bekor qilndi.!", reply_markup=fakultets_menu)
    else:
        await message.answer("Sizning xabaringiz Bekor qilndi.!", reply_markup=tyutors_menu)


@dp.message_handler(text="Bo'limga xabar")
async def ask_support(message: types.Message):
    await message.answer("Iltimos, xabar yozishda tushunarli va aniq qlib yozing.", reply_markup=ReplyKeyboardRemove())
    text = "<b>Xabar yozish yoki bekor qilish uchun quyidagi tugmani bosing!</b>"
    keyboard = await support_keyboard(messages="one")
    await message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(support_callback.filter(messages="one"))
async def send_to_support(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    user_id = int(callback_data.get("user_id"))

    await call.message.answer("Xabar kiriting va yuboring\nAks xolda bo'lsa /cancel tugmasini bosing")
    await state.set_state("wait_for_support_message")
    await state.update_data(second_id=user_id, )
    await state.update_data(mention=call.from_user.get_mention(as_html=True))

@dp.message_handler(state="wait_for_support_message", content_types=types.ContentTypes.ANY)
async def get_support_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    with open("zamdekans.txt", "r") as f:
        passwords = [line.strip() for line in f.readlines()]
    mention = data.get("mention")
    second_id = data.get("second_id")
    if message.from_user.id == 2051502101:
        await bot.send_message(second_id,
                               f"@ADU_Tyutorlar_bot sizga xabar yubordi! Quyidagi tugmani bosish orqali xabarga javob berishingiz mumkin.")
    else:
        await bot.send_message(second_id,
                               f"{mention} sizga xabar yubordi! Quyidagi tugmani bosish orqali xabarga javob berishingiz mumkin.")
    keyboard = await support_keyboard(messages="one", user_id=message.from_user.id)
    await message.copy_to(second_id, reply_markup=keyboard)
    if message.from_user.id == 2051502101:
        await message.answer("Sizning xabaringiz yuborildi!", reply_markup=fakultets_menu)
    elif message.from_user.id in passwords:
        await message.answer("Sizning xabaringiz yuborildi!", reply_markup=fakultets_menu)
    else:
        await message.answer("Sizning xabaringiz yuborildi!", reply_markup=tyutors_menu)
    await state.reset_state()
