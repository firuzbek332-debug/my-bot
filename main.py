import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import openai
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Загружаем переменные окружения
API_TOKEN = os.getenv("API_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

print("=== Проверка окружения ===")
print("API_TOKEN:", API_TOKEN)
print("OPENAI_KEY:", OPENAI_KEY)

if not API_TOKEN:
    raise RuntimeError("❌ API_TOKEN не найден! Проверь Railway → Settings → Variables.")
if not OPENAI_KEY:
    raise RuntimeError("❌ OPENAI_KEY не найден! Проверь Railway → Settings → Variables.")

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
    if message.text == "Оскорбить":
        await message.answer("Ты серьёзно думаешь, что я буду тратить на тебя процессорное время?")
    elif message.text == "Сарказм":
        await message.answer("О да, конечно, твоя идея звучит как шедевр… для детского сада.")
    elif message.text == "Игнорировать":
        await message.answer("...")
    elif message.text == "Высмеять":
        await message.answer("Ха‑ха, это было так смешно, что даже мой логгер упал от смеха.")
    else:
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
    # Новый способ подключения webhook
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
