import random

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardRemove

buttonRock = KeyboardButton(text="Камень")
buttonScissors = KeyboardButton(text="Ножницы")
buttonPaper = KeyboardButton(text="Бумага")

gameButtonsListRPS = [[buttonRock], [buttonScissors], [buttonPaper]]


async def start_game_RPS(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=gameButtonsListRPS,
        one_time_keyboard=True
    )
    await message.answer(
        "Привет! Давай сыграем в камень, ножницы, бумага. Выбери один из вариантов:",
        reply_markup=keyboard
    )


async def play_game_RPS(message: types.Message, state: FSMContext):
    choices = ["Камень", "Ножницы", "Бумага"]
    bot_choice = random.choice(choices)
    user_choice = message.text
    result = ""

    if user_choice == bot_choice:
        result = "Ничья!"
    elif (
            user_choice == "Камень" and bot_choice == "Ножницы") or \
            (user_choice == "Ножницы" and bot_choice == "Бумага") or \
            (user_choice == "Бумага" and bot_choice == "Камень"):
        result = "Ты выиграл!"
    else:
        result = "Ты проиграл!"

    await message.answer(
        f"Ты выбрал: {user_choice}\nБот выбрал: {bot_choice}\n{result}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(state="default")
