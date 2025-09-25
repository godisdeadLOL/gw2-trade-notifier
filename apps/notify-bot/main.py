import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BotCommand
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter, Command, CommandObject

from dotenv import load_dotenv
from faststream.redis import RedisBroker

from shared import (
    InitUserRequest,
    UserSyncedPayload,
    response_adapter,
    SuccessResponse,
    DeleteUserRequest,
    ErrorResponse,
)
from utils import format_updates

load_dotenv()

broker = RedisBroker(os.environ["REDIS_URL"])

bot = Bot(token=os.environ["TELEGRAM_TOKEN"])
dp = Dispatcher()


@dp.error(ExceptionTypeFilter(Exception), F.update.message.as_("message"))
async def handle_exception(event, message: Message):
    await message.answer("При работе бота произошла ошибка")


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


@dp.message(Command("start"))
async def handle_start(message: Message):
    await message.answer("да")


@dp.message(Command("token"))
async def handle_init_user(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Укажите токен")
        return

    token = command.args
    user_id = str(message.chat.id)

    status_message = await message.answer("Проверка токена...")

    try:
        redis_message = await broker.request(InitUserRequest(user_id=user_id, token=token), "user_init")
        response = response_adapter.validate_python(await redis_message.decode())
    except:
        response = None

    if response is None or isinstance(response, ErrorResponse):
        await status_message.edit_text(f"Ошибка при установке токена")
    else:
        await status_message.edit_text("Токен успешно установлен")


@dp.message(Command("clear"))
async def handle_delete_user(message: Message):
    user_id = str(message.chat.id)

    try:
        redis_message = await broker.request(DeleteUserRequest(user_id=user_id), "user_delete")
        response = response_adapter.validate_python(await redis_message.decode())
    except:
        response = None

    if response is None or isinstance(response, ErrorResponse):

        await message.answer(f"Ошибка при удалении токена")
    else:
        await message.answer("Токен удален")


@dp.startup()
async def startup():
    await bot.set_my_commands(
        [
            BotCommand(command="token", description="Установить api токен"),
            BotCommand(command="clear", description="Сбросить api токен"),
        ]
    )
    await broker.start()


@dp.shutdown()
async def shutdown():
    await broker.stop()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
