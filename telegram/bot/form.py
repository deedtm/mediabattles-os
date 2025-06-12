from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    admin_msg = State()
    prize = State()
    