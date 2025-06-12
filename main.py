from logging_utils import disable_logging
import asyncio
import sys
from telegram.bot import MediaBattleBot
from telegram.channel import Poster
from config.telegram import BOT_ARGS, POSTER_ARGS


async def main():
    mediabattle_bot = MediaBattleBot(*BOT_ARGS)
    poster = Poster(mediabattle_bot.bot, *POSTER_ARGS)
    disable_logging("aiogram.event")
    await asyncio.gather(mediabattle_bot.start(), poster.start())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
