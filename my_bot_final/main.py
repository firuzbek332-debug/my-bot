import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# 1. ТВОЙ ТОКЕН
TOKEN = "8659093719:AAFgYCwcLSAJyxVgW-Zto415p55lUlspAWw"

# 2. ВОПРОСЫ ДЛЯ ЗАДАНИЙ
QUIZ_DATA = [
    {
        "question": "Как в Python вывести текст в консоль?",
        "options": ["print()", "echo()", "say()"],
        "correct": "print()"
    },
    {
        "question": "Какой тип данных используется для целых чисел?",
        "options": ["int", "str", "float"],
        "correct": "int"
    }
]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработка команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="Услуги")
    builder.button(text="Цены")
    builder.button(text="Задание 🎮")
    builder.adjust(2)
    await message.answer("Всё очищено! Я готов к работе. Выбери действие:", 
                         reply_markup=builder.as_markup(resize_keyboard=True))

# Кнопка "Услуги"
@dp.message(F.text == "Услуги")
async def text_services(message: types.Message):
    await message.answer("Наши услуги: создание ботов любой сложности.")

# Кнопка "Цены"
@dp.message(F.text == "Цены")
async def text_price(message: types.Message):
    await message.answer("Цены начинаются от 3000 рублей.")

# Кнопка или команда для Задания
@dp.message(F.text == "Задание 🎮")
@dp.message(Command("quest"))
async def start_quiz(message: types.Message):
    item = random.choice(QUIZ_DATA)
    builder = InlineKeyboardBuilder()
    
    # Перемешиваем варианты
    options = item["options"].copy()
    random.shuffle(options)
    
    for opt in options:
        status = "yes" if opt == item["correct"] else "no"
        builder.button(text=opt, callback_data=f"quiz_{status}")
    
    builder.adjust(1)
    await message.answer(f"Вопрос: {item['question']}", reply_markup=builder.as_markup())

# Проверка ответа (нажатие на инлайн-кнопку)
@dp.callback_query(F.data.startswith("quiz_"))
async def check_answer(callback: types.CallbackQuery):
    if "yes" in callback.data:
        await callback.message.edit_text("✅ Верно! Отличная работа!")
    else:
        await callback.message.edit_text("❌ Неправильно. Попробуй еще раз!")
    await callback.answer()

# Хендлер для всего остального (должен быть последним)
@dp.message()
async def echo_all(message: types.Message):
    await message.answer("Используй кнопки в меню или команду /quest")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
