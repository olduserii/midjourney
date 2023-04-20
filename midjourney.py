import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
import discord
from discord.ext import commands

# Используйте свой токен для Telegram бота
API_TOKEN = '6149444852:AAH66hYj3mWx35GIIFMDFwO0TVUyO6SiFyM'

# Используйте свой токен для Discord
DISCORD_TOKEN = 'OTcyODEzODgzODkyOTg1ODY2.G97TpQ.ddONk5_Uu7g-ABzgIuL7mb7QrOlEFqw3aBLflY'
DISCORD_CHANNEL_ID = 1096967452283375659  # Замените на ID текстового канала Discord

logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Инициализация Discord бота
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
discord_bot = commands.Bot(command_prefix="!", intents=intents)

discord_user_responses = {}


async def on_ready():
    print(f"Discord bot is ready: {discord_bot.user}")


discord_bot.add_listener(on_ready)


async def send_message_to_discord(text):
    channel = discord_bot.get_channel(DISCORD_CHANNEL_ID)
    return await channel.send(text)


async def send_message_to_telegram(chat_id, text):
    await bot.send_message(chat_id, text)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправьте мне сообщение, и я передам его в Discord.")


@dp.message_handler()
async def echo(message: types.Message):
    try:
        discord_message = await send_message_to_discord(f"{message.chat.id}: {message.text}")
        discord_user_responses[discord_message.id] = message.chat.id
    except Exception as e:
        logging.exception("Ошибка при отправке сообщения")
        await send_message_to_telegram(message.chat.id, f"Произошла ошибка: {e}")


@discord_bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith(discord_bot.command_prefix):
        return

    if message.channel.id == DISCORD_CHANNEL_ID:
        response_to = discord_user_responses.get(message.reference.message_id)
        if response_to:
            await send_message_to_telegram(response_to, f"{message.author}: {message.content}")


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, on_startup=discord_bot.start(DISCORD_TOKEN), on_shutdown=discord_bot.close())
