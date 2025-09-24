import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode

from dotenv import load_dotenv
from faststream.redis import RedisBroker

from shared import InitUserRequest, UserSyncedPayload
from utils import format_updates

load_dotenv()

broker = RedisBroker(os.environ["REDIS_URL"])

bot = Bot(token=os.environ["TELEGRAM_TOKEN"])
dp = Dispatcher()


@broker.subscriber("error")
async def handle_error(payload):
    (user_id, msg) = payload
    chat_id = int(user_id)
    await bot.send_message(chat_id, f"Ошибка при работе бота: {msg}")


@broker.subscriber("user_inited")
async def handle_user_inited(user_id : str):
    chat_id = int(user_id)
    await bot.send_message(chat_id, "Api токен установлен")


@broker.subscriber(list="user_synced")
async def handle_user_synced(payload: UserSyncedPayload):
    if len(payload.bought) == 0 and len(payload.sold) == 0:
        return

    message = ""
    if len(payload.bought) > 0:
        message += "*Куплено:*\n"
        message += format_updates(payload.bought)
        message += "\n"

    if len(payload.sold) > 0:
        message += "*Продано:*\n"
        message += format_updates(payload.sold)
        message += "\n"

    chat_id = int(payload.user_id)
    await bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN_V2)


@dp.message()
async def handle_message(message: Message):
    init_command = "/token"

    if not message.text or not message.text.startswith(init_command):
        return

    token = message.text.replace(f"{init_command} ", "").strip()
    user_id = str(message.chat.id)

    await broker.publish(InitUserRequest(user_id=user_id, token=token), "user_init")


@dp.startup()
async def startup():
    await broker.start()


@dp.shutdown()
async def shutdown():
    await broker.stop()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
