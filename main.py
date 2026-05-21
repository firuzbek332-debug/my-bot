import asyncio
from aiogram import Bot, Dispatcher, types
import openai

API_TOKEN = "8659093719:AAFgYCwcLSAJyxVgW-Zto415p55lUlspAWw"
OPENAI_KEY = "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"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

openai.api_key = OPENAI_KEY

@dp.message()
async def handle_message(message: types.Message):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Отвечай грубо и саркастично: {message.text}",
        max_tokens=150,
        temperature=0.9
    )
    await message.answer(response.choices[0].text.strip())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
