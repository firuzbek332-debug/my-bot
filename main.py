import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Вставь сюда свой токен от BotFather
TOKEN = "8659093719:AAFgYCwcLSAJyxVgW-Zto415p55lUlspAWw"

# 7 Обучающих вопросов (ты можешь заменить их своими)
QUIZ_DATA = [
    {"question": "Как вывести текст в консоль в Python?", "options": ["print()", "echo()", "say()"], "correct": "print()"},
    {"question": "Какой тип данных используется для целых чисел?", "options": ["int", "str", "float"], "correct": "int"},
    {"question": "Какой символ используется для комментариев в Python?", "options": ["#", "//", "/*"], "correct": "#"},
    {"question": "Какое имя переменной написано правильно?", "options": ["my_var", "1var", "my-var"], "correct": "my_var"},
    {"question": "Что делает функция len() в Python?", "options": ["Возвращает длину", "Складывает числа", "Удаляет данные"], "correct": "Возвращает длину"},
    {"question": "Как правильно начать цикл 'while' в Python?", "options": ["while x < 5:", "while x < 5", "while (x < 5)"], "correct": "while x < 5:"},
    {"question": "Какое ключевое слово создает функцию?", "options": ["def", "function", "create"], "correct": "def"}
]

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояние для отслеживания игры и защиты от обнуления
class QuizStates(StatesGroup):
    in_game = State()

# Временное хранилище данных пользователей
user_data = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear() # Сброс состояния при перезапуске
    
    builder = ReplyKeyboardBuilder()
    builder.button(text="Услуги")
    builder.button(text="Цены")
    builder.button(text="Квест 🎮")
    builder.adjust(2)
    
    await message.answer(
        "Добро пожаловать! Выберите действие ниже. Нажмите 'Квест 🎮', чтобы начать испытание из 7 вопросов!", 
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(F.text == "Услуги")
async def text_services(message: types.Message):
    await message.answer("Наши услуги: создание ботов любой сложности.")

@dp.message(F.text == "Цены")
async def text_price(message: types.Message):
    await message.answer("Цены начинаются от 3000 рублей / эквивалент.")

# Старт Квеста
@dp.message(F.text == "Квест 🎮")
async def start_quiz(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Создаем профиль, если пользователя еще нет
    if user_id not in user_data:
        user_data[user_id] = {"tokens": 0}
        
    # Сброс и запуск заново при каждом нажатии (Анти-чит)
    user_data[user_id]["lives"] = 3
    user_data[user_id]["current_question"] = 0
    
    # Перемешиваем вопросы для этой попытки
    shuffled_quiz = QUIZ_DATA.copy()
    random.shuffle(shuffled_quiz)
    user_data[user_id]["questions"] = shuffled_quiz[:7]
    
    await state.set_state(QuizStates.in_game)
    await ask_question(message, user_id)

async def ask_question(message: types.Message, user_id: int):
    data = user_data[user_id]
    q_index = data["current_question"]
    
    # Если прошел все 7 вопросов
    if q_index >= 7:
        data["tokens"] += 10
        await message.answer(f"🎉 ПОЗДРАВЛЯЕМ! Вы ответили на все 7 вопросов!\n💰 Вы выиграли 10 жетонов! Всего: {data['tokens']} 🪙")
        return
        
    question_item = data["questions"][q_index]
    
    builder = InlineKeyboardBuilder()
    options = question_item["options"].copy()
    random.shuffle(options) # Перемешиваем варианты ответов
    
    for opt in options:
        is_correct = "1" if opt == question_item["correct"] else "0"
        # Передаем индекс вопроса, чтобы нельзя было нажимать старые кнопки
        builder.button(text=opt, callback_data=f"q_{q_index}_{is_correct}")
        
    builder.adjust(1)
    
    lives_heart = "❤️" * data["lives"]
    await message.answer(
        f"Уровень {q_index + 1}/7\nЖизни: {lives_heart}\n\nВопрос: {question_item['question']}", 
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data.startswith("q_"), QuizStates.in_game)
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if user_id not in user_data:
        await callback.answer("Сессия потеряна. Нажмите Квест заново!")
        return

    parts = callback.data.split("_")
    q_index = int(parts[1])
    is_correct = parts[2] == "1"
    
    # Проверка: не пытается ли пользователь нажать на старое сообщение
    if q_index != user_data[user_id]["current_question"]:
        await callback.answer("Нельзя хитрить и нажимать старые кнопки! 😉")
        return
        
    if is_correct:
        user_data[user_id]["current_question"] += 1
        await callback.message.edit_text("✅ Верно! Переходим к следующему...")
        await ask_question(callback.message, user_id)
    else:
        user_data[user_id]["lives"] -= 1
        
        # Если кончились жизни
        if user_data[user_id]["lives"] <= 0:
            await state.clear() # Сбрасываем статус игры
            await callback.message.edit_text(
                "❌ Неверно! Игра окончена. У вас закончились жизни 💔\nЧтобы попробовать снова, нажмите кнопку 'Квест 🎮'."
            )
        else:
            # Ошибся, но жизни еще есть — просто идем к следующему вопросу
            user_data[user_id]["current_question"] += 1
            await callback.message.edit_text(f"❌ Неверно! Вы потеряли жизнь.")
            await ask_question(callback.message, user_id)
            
    await callback.answer()

@dp.message()
async def echo_all(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    # Если пользователь пишет текст во время игры
    if current_state == QuizStates.in_game.state:
        await message.answer("Сначала завершите квест! Для принудительного сброса введите /start.")
    else:
        await message.answer("Используйте кнопки меню или команду /start")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
