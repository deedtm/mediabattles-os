from . import config
from dt_utils import strings_to_datetimes, string_to_time
from aiogram.client.default import DefaultBotProperties

# Bot
TOKEN = config.get("telegram", "token")
PM = config.get("telegram", "parse_mode")
IS_LINK_PREVIEW_DISABLED = config.getboolean("telegram", "link_preview_is_disabled")
BOT_ARGS = TOKEN, DefaultBotProperties(
    parse_mode=PM, link_preview_is_disabled=IS_LINK_PREVIEW_DISABLED
)

# Poster
CHANNEL_ID = int(config.get("telegram", "channel_id"))
BOT_USERNAME = config.get("telegram", "bot_username")
ADMINS_IDS = list(map(int, config.get("telegram", "admins_ids").split(", ")))

__times_strs = config.get("posting", "times").split(", ")
TIME_FORMAT = config.get("posting", "times_format")
SCHEDULE = strings_to_datetimes(__times_strs, TIME_FORMAT)

__before_battle_time = config.get("battle", "before_time")
__rounds_interval = config.get("battle", "rounds_interval")
BEFORE_BATTLE_TIME = string_to_time(__before_battle_time, TIME_FORMAT)
ROUNDS_INTERVAL = string_to_time(__rounds_interval, TIME_FORMAT)

__auction_duration = config.get("auction", "duration")
AUCTION_ROUNDS = config.getint("auction", "rounds")
AUCTION_DURATION = string_to_time(__auction_duration, TIME_FORMAT)

POSTER_ARGS = (
    CHANNEL_ID,
    BOT_USERNAME,
    ADMINS_IDS,
    SCHEDULE,
    TIME_FORMAT,
    BEFORE_BATTLE_TIME,
    ROUNDS_INTERVAL,
    AUCTION_ROUNDS,
    AUCTION_DURATION,
)

# Other
EMOJI_ID_LEN = config.getint('emojiid', 'id_length')
CHANNEL_USERNAME = config.get('telegram', 'channel_username')
ADMINS_IDS = list(map(int, config.get('telegram', 'admins_ids').split(', ')))
