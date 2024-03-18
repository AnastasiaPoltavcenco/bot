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

#from pymorphy2 import MorphAnalyzer

my_id = 999030930

router = Router()
router.message.filter(F.chat.type == "supergroup", F.from_user.id == my_id)
dp = Dispatcher()

#morph = MorphAnalyzer(lang="ru")
triggers = ["дурак", "козёл", "коза"]


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


async def main() -> None:
    bot = Bot(open("TOKEN.txt").read(), parse_mode=ParseMode.HTML)

    dp.include_router(router)

    await  bot.delete_webhook(True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
