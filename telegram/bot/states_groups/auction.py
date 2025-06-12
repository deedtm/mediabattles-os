from aiogram.fsm.state import State, StatesGroup


class AuctionWait(StatesGroup):
    value = State("auction:value")
    