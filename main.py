import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

# ⚠️ ВСТАВЬ СВОИ ДАННЫЕ СЮДА
TOKEN = "1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ"
USERNAME = "твой_ник" # Напиши сюда свой ник в Телеграм без значка @

QUIZ_DATA = [
    {"question": "Как вывести текст в консоль в Python?", "options": ["print()", "echo()", "say()"], "correct": "print()"},
    {"question": "Какой тип данных используется для целых чисел?", "options": ["int", "str", "float"], "correct": "int"},
    {"question": "Какой символ используется для комментариев в Python?", "options": ["#", "//", "/*"], "correct": "#"},
    {"question": "Какое имя переменной написано правильно?", "options": ["my_var", "1var", "my-var"], "correct": "my_var"},
    {"question": "Что делает функция len() в Python?", "options": ["Возвращает длину", "Складывает числа", "Удаляет данные"], "correct": "Возвращает длину"},
    {"question": "Как правильно начать цикл 'while' в Python?", "options": ["while x < 5:", "while x < 5", "while (x < 5)"], "correct": "while x < 5:"},
    {"question": "Какое ключевое слово создает функцию?", "options": ["def", "function", "create"], "correct": "def"}
]

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

class QuizStates(StatesGroup):
    in_game = State()

user_data = {}

def get_progress_bar(current, total=7):
    filled = "🟩" * current
    empty = "⬜" * (total - current)
    return f"{filled}{empty} ({current}/{total})"

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(1)
    
    builder = ReplyKeyboardBuilder()
    builder.button(text="📂 Наши Услуги")
    builder.button(text="💳 Цены")
    builder.button(text="🚀 Начать Квест")
    builder.button(text="👤 Мой Профиль")
    builder.adjust(2, 2)
    
    await message.answer(
        "<b>👋 Добро пожаловать в Академию Будущего!</b>\n\n"
        "Здесь ты сможешь проверить свои знания в программировании и заработать реальные жетоны.\n\n"
        "<i>Нажми кнопку '🚀 Начать Квест', чтобы начать испытание!</i>", 
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(F.text == "📂 Наши Услуги")
async def text_services(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="👨‍💻 Обсудить проект", url=f"https://t.me{USERNAME}")
    
    await message.answer(
        "🛠 <b>Наши Услуги</b>\n\n"
        "Мы создаем профессиональных ботов любой сложности под ключ 🔑\n\n"
        "🔹 <b>Визитки и Автоответчики</b>\n"
        "<i>(Бот расскажет о вас и ответит на частые вопросы)</i>\n\n"
        "🔹 <b>Магазины и Доставка</b>\n"
        "<i>(Каталог товаров, корзина и прием оплаты картой)</i>\n\n"
        "🔹 <b>Игры и Квесты</b>\n"
        "<i>(Как наша мини-игра: с жизнями, жетонами и рекордами!)</i>\n\n"
        "🔹 <b>Автоматизация</b>\n"
        "<i>(Рассылки, парсинг данных, учет клиентов)</i>\n\n"
        "👉 Нажми кнопку ниже, чтобы рассказать о своей идее!",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

@dp.message(F.text == "💳 Цены")
async def text_price(message: types.Message):
    await message.answer(
        "💳 <b>Стоимость Разработки</b>\n\n"
        "Итоговая цена зависит от сложности функций. Вот ориентировочные пакеты:\n\n"
        "🟢 <b>Пакет «Старт»</b> — от 1 500 ₽\n"
        "<i>(Простой бот-визитка, меню, кнопки, текст)</i>\n\n"
        "🟡 <b>Пакет «Бизнес»</b> — от 5 000 ₽\n"
        "<i>(База данных, сохранение пользователей, сложные сценарии)</i>\n\n"
        "🔴 <b>Пакет «Про»</b> — от 10 000 ₽\n"
        "<i>(Магазины, платежные системы, сложные игровые механики)</i>\n\n"
        "💬 <i>Точная стоимость рассчитывается индивидуально после обсуждения ТЗ.</i>",
        parse_mode=ParseMode.HTML
    )

@dp.message(F.text == "👤 Мой Профиль")
async def text_profile(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"tokens": 0, "best_score": 0}
        
    tokens = user_data[user_id].get("tokens", 0)
    best = user_data[user_id].get("best_score", 0)
    
    await message.answer(
        "📊 <b>Ваш Профиль</b>\n\n"
        f"👤 <b>Пользователь:</b> {message.from_user.first_name}\n"
        f"🪙 <b>Баланс жетонов:</b> {tokens} шт.\n"
        f"🏆 <b>Лучший результат:</b> {best}/7 уровней",
        parse_mode=ParseMode.HTML
    )

@dp.message(F.text == "🚀 Начать Квест")
async def start_quiz(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        user_data[user_id] = {"tokens": 0, "best_score": 0}
        
    user_data[user_id]["lives"] = 3
    user_data[user_id]["current_question"] = 0
    
    shuffled_quiz = QUIZ_DATA.copy()
    random.shuffle(shuffled_quiz)
    user_data[user_id]["questions"] = shuffled_quiz[:7]
    
    await state.set_state(QuizStates.in_game)
    await ask_question(message, user_id)

async def ask_question(message: types.Message, user_id: int):
    data = user_data[user_id]
    q_index = data["current_question"]
    
    if q_index > data.get("best_score", 0):
        data["best_score"] = q_index
    
    if q_index >= 7:
        data["tokens"] += 10
        await message.answer(
            "<b>🎉 ПОЗДРАВЛЯЕМ!</b>\n\n"
            "Ты успешно ответил на все 7 вопросов и доказал свой профессионализм!\n\n"
            "💰 <b>Награда:</b> +10 жетонов 🪙",
            parse_mode=ParseMode.HTML
        )
        return
        
    question_item = data["questions"][q_index]
    
    builder = InlineKeyboardBuilder()
    options = question_item["options"].copy()
    random.shuffle(options)
    
    for opt in options:
        is_correct = "1" if opt == question_item["correct"] else "0"
        builder.button(text=opt, callback_data=f"q_{q_index}_{is_correct}")
        
    builder.adjust(1)
    
    lives_heart = "❤️" * data["lives"]
    progress = get_progress_bar(q_index)
    
    await message.answer(
        f"<b>🎯 Квест: Уровень {q_index + 1}</b>\n"
        f"Прогресс: {progress}\n"
        f"Жизни: {lives_heart}\n\n"
        f"<b>Вопрос:</b> {question_item['question']}", 
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(F.data.startswith("q_"), QuizStates.in_game)
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if user_id not in user_data:
        await callback.answer("Сессия потеряна. Попробуй заново!")
        return

    parts = callback.data.split("_")
    q_index = int(parts)
    is_correct = parts == "1"
    
    if q_index != user_data[user_id]["current_question"]:
        await callback.answer("Нельзя хитрить и нажимать старые кнопки! 😉")
        return
        
    if is_correct:
        user_data[user_id]["current_question"] += 1
        await callback.message.edit_text("⚡️ <b>Верно!</b> Загружаем следующий уровень...", parse_mode=ParseMode.HTML)
        await asyncio.sleep(0.5)
        await ask_question(callback.message, user_id)
    else:
        user_data[user_id]["lives"] -= 1
        
        if user_data[user_id]["lives"] <= 0:
            await state.clear()
            await callback.message.edit_text(
                "💔 <b>Игра окончена!</b>\n\n"
                "К сожалению, у тебя закончились жизни. Попробуй пройти квест ещё раз, нажав кнопку в меню.",
                parse_mode=ParseMode.HTML
            )
        else:
            user_data[user_id]["current_question"] += 1
            await callback.message.edit_text("❌ <b>Неверно!</b> Ты потерял жизнь.", parse_mode=ParseMode.HTML)
            await asyncio.sleep(0.5)
            await ask_question(callback.message, user_id)
            
    await callback.answer()

@dp.message()
async def echo_all(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == QuizStates.in_game.state:
        await message.answer("🤫 <b>Сфокусируйся на квесте!</b> Сначала заверши игру.", parse_mode=ParseMode.HTML)
    else:
        await message.answer("🔮 Пожалуйста, воспользуйся кнопками меню ниже.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
