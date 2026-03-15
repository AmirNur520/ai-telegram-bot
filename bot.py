import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI
from keyboard import main_menu

from config import BOT_TOKEN, GROQ_API_KEY
from database import add_user

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_context = {}

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

@dp.message(Command("start"))
async def start(message: types.Message):
    add_user(message.from_user.id)
    await message.answer("🤖 Привет!\n\n" 
                         "Я AI помощник.\n"  
                         "Выберите функцию ниже 👇",
                         reply_markup=main_menu)
    
@dp.message(Command("clear"))
async def clear_context(message: types.Message):
   user_context.pop(message.from_user.id, None)
   await message.answer("🧠 Память диалога очищена.") 
    
@dp.message(lambda message: message.text == "ℹ️ Помощь")  
async def help_menu(message: types.Message):
    await message.answer(
        "Я могу помочь вам с различными задачами, такими как:\n"
        "🤖 отвечать на вопросы\n"
        "💻 помогать с кодом\n"
        "🌍 переводить текст\n"
        "🧠 генерировать идеи"
    )

@dp.message(lambda message: message.text == "🧠 Идеи")
async def ideas(message: types.Message):
    prompt = "Предложите 5 креативных идей для стартапов в сфере технологий."

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    await message.answer(response.choices[0].message.content)

@dp.message(lambda message: message.text == "🌍 Перевод")
async def translate(message: types.Message):
    await message.answer("Напишите текст, и я переведу его.")

@dp.message(lambda message: message.text == "💻 Помощь с кодом")
async def code_help(message: types.Message):
    await message.answer("Отправьте код или вопрос по программированию.")        
    
@dp.message()
async def ai_chat(message: types.Message):

    user_id = message.from_user.id
    if user_id not in user_context:
        user_context[user_id] = [
            {"role": "system", "content": "Ты - полезный и дружелюбный AI помощник."}
        ]

    user_context[user_id].append(
        {"role": "user", "content": message.text}
    )    

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=user_context[user_id]
        )

        ai_text = response.choices[0].message.content

        user_context[user_id].append(
            {"role": "assistant", "content": ai_text}
        )

        await message.answer(ai_text)

    except Exception as e:
      await message.answer("Извините, произошла ошибка при обработке вашего запроса.")
      print(f"Ошибка Groq: {e}")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    