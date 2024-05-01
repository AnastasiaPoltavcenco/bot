from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from strings import *

button1 = KeyboardButton(text=rock_Paper_Scissors)
button2 = KeyboardButton(text=wheel_of_Fortune)
button3 = KeyboardButton(text=random_number)
button4 = KeyboardButton(text=quiz)

gameButtonsList = [[button1], [button2], [button3], [button4]]
gameButtonsReplyMarkup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=gameButtonsList, one_time_keyboard=True)
