import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from os import listdir
from ..objects import router
from .__utils import save_handled_requests
from . import users_handlers, admins_handlers


class MediaBattleBot:
    def __init__(self, token: str, default: DefaultBotProperties):
        self.bot = Bot(token=token, default=default)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.dp.include_router(router)

        if "handled_requests.json" not in listdir("telegram/bot"):
            save_handled_requests({})

    async def start(self):
        logging.info(f"Starting {self.__class__.__name__}...")

        bot, dp = self.bot, self.dp
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
