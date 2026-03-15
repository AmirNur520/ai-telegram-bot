from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🤖 AI чат")],
        [KeyboardButton(text="💻 Помощь с кодом"), KeyboardButton(text="🌍 Перевод")],
        [KeyboardButton(text="🧠 Идеи"), KeyboardButton(text="ℹ️ Помощь")],
    ],
    resize_keyboard=True
)