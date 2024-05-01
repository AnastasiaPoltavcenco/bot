import re
import asyncio
import sys

import joblib

from typing import Any
from datetime import datetime, timedelta
from contextlib import suppress

from aiogram import types
from aiogram import Router, Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ChatPermissions
from aiogram.filters import Command, CommandObject
from aiogram.enums import ParseMode, ChatType
from aiogram.exceptions import TelegramBadRequest

from env import *
from sys_messages import *
from utils import *
from buttons import *
from rock_Paper_Scissors import *
from randomize_num import *

#############################################


router = Router()
router.message.filter(F.chat.type == "supergroup")

bot = Bot(open("TOKEN.txt").read(), parse_mode=ParseMode.HTML)

dp = Dispatcher()


##########################################


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
    if not is_owner(message.from_user.id):
        return await message.reply(access_denied_msg)
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


@router.message(Command("unban"))
async def unban_command(message: types.Message):
    if not is_owner(message.from_user.id):
        return await message.reply(access_denied_msg)
    try:
        user_id = int(message.text.split()[1])
        await unban_user(user_id)
    except IndexError:
        await message.reply("Используйте команду так: /unban user_id")


@router.message(Command("unmute"))
async def mute(message: Message, bot: Bot, command: CommandObject | None = None) -> Any:
    reply = message.reply_to_message
    if not is_owner(message.from_user.id):
        return await message.reply(access_denied_msg)
    if not reply:
        return await message.answer(user_not_found_msg)

    mention = reply.from_user.mention_html(reply.from_user.first_name)

    with suppress(TelegramBadRequest):
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=reply.from_user.id,
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
        await message.answer(f"{mention} " + user_unmuted_msg)


@router.message(Command("mute"))
async def mute(message: Message, bot: Bot, command: CommandObject | None = None) -> Any:
    reply = message.reply_to_message
    if not is_owner(message.from_user.id):
        return await message.reply(access_denied_msg)
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


# --------------------------  GAMES  ---------------------------
games_list = []


@router.message(lambda message: message.text.startswith('/любимые игры'))
async def show_fav_games(message: types.Message) -> Any:
    fav_games = []
    with open('fav_games.txt', 'r') as file:
        for line in file:
            if line:
                fav_games.append(line.strip())
    await message.answer(FavGameAdd_request_answer)
    await message.answer("Любимые игры:")
    if len(fav_games) > 0:
        return await message.answer("\n".join(fav_games))
    else:
        return await message.answer("Список любимых игр пуст.")


@router.message(lambda message: message.text.startswith('/добавь игру'))
async def add_game_to_fav(message: types.Message) -> Any:
    game_name = message.text.split('/добавь игру ', 1)[1]
    games_list.append(game_name)
    with open('fav_games.txt', 'a') as file:
        file.write(f'{game_name}\n')\


@router.message(lambda message: message.text.startswith('/удали игру'))
async def remove_game_from_fav(message: types.Message) -> Any:
    game_name = message.text.split('/удали игру ', 1)[1]
    with open('fav_games.txt', 'r') as file:
            lines = file.readlines()
    print(lines)
    print(game_name)
    if len(lines) == 0:
        return await message.answer("Список любимых игр пуст.")
    if (game_name + "\n") not in lines:
        await message.answer(f"Игры '{game_name}' нет в списке.")
        return

    lines = [line.strip() for line in lines if line.strip() != game_name]

    with open('fav_games.txt', 'w') as file:
        file.writelines("\n".join(lines))

    await message.answer(f"Игра '{game_name}' удалена из списка любимых.")


@router.message(Command("играть"))
async def choose_game(message: Message) -> Any:
    await message.answer("Привет, выбери игру:", reply_markup=gameButtonsReplyMarkup)


@router.message(F.text == quiz)
async def game1(message: types.Message):
    await message.answer(chosen_the_quiz)


@router.message(F.text == wheel_of_Fortune)
async def game2(message: types.Message):
    await message.answer(chosen_the_wheel_of_Fortune)


@router.message(F.text == random_number)
async def game3(message: types.Message):
    await message.answer(chosen_the_random_number + ": " + str(await( start_random_num_game())))


@router.message(F.text == rock_Paper_Scissors)
async def game3(message: types.Message):
    await message.answer(chosen_the_rock_Paper_Scissors)
    await start_game_RPS(message)


@router.message(lambda message: message.text in ["Камень", "Ножницы", "Бумага"])
async def play(message: types.Message, state: FSMContext):
    await play_game_RPS(message, state)


async def main() -> None:
    dp.include_router(router)

    await bot.delete_webhook(True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
