################################DOCUMENTATION###################################

6x# FILE - name of file
** - before function
*** - before variable
(...) - comment


###### FILE rock_Paper_Scissors.py
(_RPS - add to the end of function\variable\list)
** function start_game_RPS:
    calls by @router.message(F.text == rock_Paper_Scissors) async def game3(message: types.Message):
    from main.py
    create keyboard and send to the user

** function play_game_RPS
   calls by @router.message(lambda message: message.text in ["Камень", "Ножницы", "Бумага"]) async def play(message: types.Message, state: FSMContext):
   from main.py
   run game logic, create bot response and send result to the user

###### FILE buttons.py
*** gameButtonsList - list of buttons
*** gameButtonsReplyMarkup - contains buttons for game

###### FILE env.py
(environments)

###### FILE sys_messages.py
( contains strings used for system messages for users
    cases:
        access denied
        user not found
        mute\unmute
        ban\unban
)

( contains response to user
    cases:
        chosen game >>>
)

###### FILE strings.py
( contains text for button's names )

###### FILE utils.py

** is_owner
    calls when need to check is owner call command or not
    calls from main.py
    return a boolean value based on received user_id == owner_id