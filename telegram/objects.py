from aiogram import Router
from battle import Battle
# from donation_api import DonationAPI
from emoji_identificator import EmojiID
from dt_utils import strings_to_datetimes
from .keyboard import Keyboard
from .bot.administration import Administration
from config.telegram import (
    TIME_FORMAT,
    SCHEDULE,
    EMOJI_ID_LEN,
    CHANNEL_USERNAME,
    ADMINS_IDS,
    __times_strs,
)


battle = Battle(SCHEDULE, TIME_FORMAT)
emojiid = EmojiID(EMOJI_ID_LEN)
kb = Keyboard(CHANNEL_USERNAME, __times_strs)
admin = Administration(kb, ADMINS_IDS)
router = Router()

# __widget_token = __config.get('donation_alerts', 'widget_token')
# dapi = DonationAPI(__widget_token)
