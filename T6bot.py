import os
import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from aiohttp import web  # для фейкового веб-сервера

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Token not found! Check .env file and BOT_TOKEN variable")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Данные канала и диапазон постов
CHANNEL_USERNAME = "@Memes_and_other_news"
MIN_POST_ID = 10
MAX_POST_ID = 10700

# Кнопки
subscribe_button = InlineKeyboardButton(
    text="Subscribe",
    url="https://t.me/Memes_and_other_news"
)
random_meme_button = InlineKeyboardButton(
    text="Random Meme",
    callback_data="random_post"
)

# Клавиатура
channel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [subscribe_button],
        [random_meme_button]
    ]
)

# /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "This bot was created with the support of the channel https://t.me/Memes_and_other_news",
        reply_markup=channel_kb
    )

# Обработка кнопки "Random Meme"
@dp.callback_query(lambda c: c.data == "random_post")
async def send_random_post(callback_query: types.CallbackQuery):
    for _ in range(10):
        random_id = random.randint(MIN_POST_ID, MAX_POST_ID)
        try:
            await bot.forward_message(
                chat_id=callback_query.from_user.id,
                from_chat_id=CHANNEL_USERNAME,
                message_id=random_id
            )
            await bot.send_message(
                chat_id=callback_query.from_user.id,
                text="Want another one? 🎯",
                reply_markup=channel_kb
            )
            await callback_query.answer()
            return
        except Exception:
            continue
    await callback_query.message.answer(
        "⚠️ Could not find an available post, please try again.",
        reply_markup=channel_kb
    )
    await callback_query.answer()

# Проверка доступа к каналу
async def check_channel_access():
    try:
        chat = await bot.get_chat(CHANNEL_USERNAME)
        print(f"✅ Bot can access the channel: {chat.title}")
    except Exception as e:
        print(f"❌ Bot cannot access the channel {CHANNEL_USERNAME}. Make sure it is an admin. Error: {e}")
        raise SystemExit

# Мини-веб-сервер для Render
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_app():
    app = web.Application()
    app.router.add_get("/", handle)
    port = int(os.environ.get("PORT", 5000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server started on port {port}")

# Основная функция
async def main():
    await check_channel_access()
    print("🚀 Bot is starting...")
    await asyncio.gather(
        start_web_app(),       # Запускаем веб-сервер
        dp.start_polling(bot)  # Запускаем бота
    )

if __name__ == "__main__":
    asyncio.run(main())
