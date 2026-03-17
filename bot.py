import asyncio
from aiogram.enums import ChatAction
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI
from database import add_user, save_message, get_messages, clear_messages
from keyboard import main_menu

from config import BOT_TOKEN, GROQ_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

@dp.message(Command("start"))
async def start(message: types.Message):
    add_user(message.from_user.id)
    name = message.from_user.first_name
    await message.answer(f"🤖 Привет, {name}!\n\n" 
                         "Я AI помощник.\n"  
                         "Выберите функцию ниже 👇",
                         reply_markup=main_menu)
    
@dp.message(Command("clear"))
async def clear_context(message: types.Message):
   clear_messages(message.from_user.id)
   await message.answer("🧠 Память диалога очищена.") 

@dp.message(Command("profile"))
async def profile(message: types.Message):
    user = message.from_user
    await message.answer(f"👤 Профиль:\n\n"
                         f"ID: {user.id}\n"
                         f"Имя: {user.first_name}\n"
                         f"Username: {user.username}"
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "🤖 Возможности бота:\n\n"
        "💬 Общение с AI\n"
        "💻 Помощь с кодом\n"
        "🌍 Перевод текста\n"
        "🧠 Генерация идей\n\n"
        "Команды:\n"
        "/clear — очистить память\n"
        "/profile — ваш профиль\n"
        "/help — помощь"
    )

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
    user_name = message.from_user.first_name

    messages = get_messages(user_id)

    if not messages:
        messages = [
            {"role": "system",
             "content": f"Ты очень умный AI помощник. Отвечай подробно и структурированно. "
               f"Пользователя зовут {user_name}. Иногда обращайся к нему по имени. "
               "Если вопрос связан с программированием - объясняй код и приводи примеры. "
               "Если вопрос общий - давай полезный развернутый ответ."
            }
        ]

    save_message(user_id, "user", message.text)
    messages.append({"role": "user", "content": message.text})


    try:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            top_p=1
        )

        ai_text = response.choices[0].message.content or "⚠️ Пустой ответ от AI"

        save_message(user_id, "assistant", ai_text)

        await message.answer(ai_text)

    except Exception as e:
      await message.answer("Извините, произошла ошибка при обработке вашего запроса.")
      print(f"Ошибка Groq: {e}")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    