from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

"""adu"""
fakultets_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="ATKI"),
            KeyboardButton(text="TARIX"),
        ],
        [
            KeyboardButton(text="MATEMATIKA"),
            KeyboardButton(text="FIZIKA"),
        ],
        [
            KeyboardButton(text="FILOLOGIYA"),
            KeyboardButton(text="JISMONIY MA'DANIYAT"),
         ],
        [
            KeyboardButton(text="IJTIMOIY IQTISODIYOT"),
            KeyboardButton(text="PEDAGOGIKA VA SAN'ATSHUNOSLIK"),
        ],
        [
            KeyboardButton(text="Bo'limga xabar"),
            KeyboardButton(text="TABIIY FANLAR"),
         ],
        [KeyboardButton(text="super_admin"),
         KeyboardButton(text="📥 Yuklash|Download"),
         ],
    ],
    resize_keyboard=True
)
super_admin_meu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Add_db"),
            KeyboardButton(text="Delete_db"),
        ],
        [
            KeyboardButton(text="Sendpost"),
            KeyboardButton(text="from_excel_to_db"),
        ],
        [
            KeyboardButton(text="🏠"),
            KeyboardButton(text="update_telegram_id"),
         ]
    ],
    resize_keyboard=True
)
tyutors_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Bo'limga xabar"),
         ],
    ],
    resize_keyboard=True
)