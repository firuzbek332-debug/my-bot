import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import openai
from aiohttp import web

# Переменные окружения (Railway → Settings → Variables)
API_TOKEN = os.getenv("8659093719:AAFgYCwcLSAJyxVgW-Zto415p55lUlspAWw")
OPENAI_KEY = os.getenv("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")

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://<invigorating-fulfillment>.up.railway.app{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
openai.api_key = OPENAI_KEY

# Клавиатура
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оскорбить"), KeyboardButton(text="Сарказм")],
        [KeyboardButton(text="Игнорировать"), KeyboardButton(text="Высмеять")]
    ],
    resize_keyboard=True
)

@dp.message()
async def handle_message(message: types.Message):
    # Если нажата кнопка — отвечаем готовым текстом
    if message.text == "Оскорбить":
        await message.answer("Ты серьёзно думаешь, что я буду тратить на тебя процессорное время?")
    elif message.text == "Сарказм":
        await message.answer("О да, конечно, твоя идея звучит как шедевр… для детского сада.")
    elif message.text == "Игнорировать":
        await message.answer("...")
    elif message.text == "Высмеять":
        await message.answer("Ха‑ха, это было так смешно, что даже мой логгер упал от смеха.")
    else:
        # Иначе — используем OpenAI для генерации саркастичного ответа
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Отвечай грубо и саркастично: {message.text}",
            max_tokens=150,
            temperature=0.9
        )
        await message.answer(response.choices[0].text.strip(), reply_markup=keyboard)

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()

def main():
    app = web.Application()
    dp.setup(app, path=WEBHOOK_PATH)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
print("API_TOKEN:", API_TOKEN)
print("API_TOKEN:", API_TOKEN)
if not API_TOKEN:
    raise RuntimeError("API_TOKEN не найден! Проверь переменные окружения.")
