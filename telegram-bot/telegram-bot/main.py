import re
import asyncio
import joblib

from typing import Any
from datetime import datetime, timedelta
from contextlib import suppress


from aiogram import types
from aiogram import Router, Bot, Dispatcher, F
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode, ChatType
from aiogram.exceptions import TelegramBadRequest


#############################################
my_id = 999030930

router = Router()
router.message.filter(F.chat.type == "supergroup", F.from_user.id == my_id)

bot = Bot(open("TOKEN.txt").read(), parse_mode=ParseMode.HTML)

dp = Dispatcher()
##########################################

rude_words = ["word1", "word2", "word3"]


def parse_time(time_string: str | None) -> datetime | None:
    if not time_string:
        return None
    match_ = re.match(
        r"(\d+)([a-z])",
        time_string.lower().strip()
    )
    current_datetime = datetime.utcnow()

    if match_:
        value = int(match_.group(1))
        unit = match_.group(2)
        match unit:
            case "h":
                time_delta = timedelta(hours=value)
            case "d":
                time_delta = timedelta(days=value)
            case "w":
                time_delta = timedelta(weeks=value)
            case _:
                return None
    else:
        return None

    new_datetime = current_datetime + time_delta
    return new_datetime


async def check_rude_words(message: Message):
    if any(word in message.text.lower() for word in rude_words):
        await muteReasonRudeWords(message, bot)


@dp.message_handler(lambda message: True)
async def handle_message(message: Message):
    await check_rude_words(message)


@router.message(Command("ban"))
async def ban(message: Message, bot: Bot, command: CommandObject | None = None) -> Any:
    reply = message.reply_to_message
    if not reply:
        return await message.answer("User not found!")
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.ban_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,  # user that has been signalized
            until_date=until_date
        )
        await message.answer(f"{mention} has been banned")


async def unban_user(user_id: int):
    global banned_users
    banned_users.discard(user_id)
    await bot.restrict_chat_member(chat_id="YOUR_CHAT_ID", user_id=user_id, permissions=ChatPermissions())
    await bot.send_message(chat_id="YOUR_CHAT_ID", text=f"Пользователь с ID {user_id} был разбанен.")


@dp.message_handler(commands=['unban'])
async def unban_command(message: types.Message):
    try:
        user_id = int(message.text.split()[1])
        await unban_user(user_id)
    except IndexError:
        await message.reply("Используйте команду так: /unban user_id")


@router.message(Command("unmute"))
async def mute(message: Message, bot: Bot, command: CommandObject | None = None) -> Any:
    reply = message.reply_to_message
    if not reply:
        return await message.answer("User not found!")
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
            until_date=until_date,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_pin_messages=True,
                can_send_audios=True,
                can_send_photos=True,
                can_send_videos=True,
                can_invite_users=True
            )
        )
        await message.answer(f"{mention} has been unmuted")


@router.message(Command("mute"))
async def mute(message: Message, bot: Bot, command: CommandObject | None = None) -> Any:
    reply = message.reply_to_message
    if not reply:
        return await message.answer("User not found!")
    until_date = parse_time(command.args)
    mention = reply.from_user.mention_html(reply.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
            until_date=until_date,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_pin_messages=False,
                can_send_audios=False,
                can_send_photos=False,
                can_send_videos=False,
                can_invite_users=False
            )
        )
        await message.answer(f"{mention} has been muted")


async def muteReasonRudeWords(message: Message, bot: Bot):
    user_id = message.from_user.id
    until_date = datetime.now() + timedelta(hours=1)
    mention = message.from_user.mention_html(message.from_user.first_name)

    try:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            until_date=until_date,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_pin_messages=False,
                can_send_audios=False,
                can_send_photos=False,
                can_send_videos=False,
                can_invite_users=False
            )
        )
        await message.answer(f"{mention} has been muted")
    except Exception as e:
        await message.answer(f"Error occurred: {e}")


async def main() -> None:

    dp.include_router(router)

    await bot.delete_webhook(True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
