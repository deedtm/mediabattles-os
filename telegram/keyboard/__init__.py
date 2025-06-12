from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.telegram import BOT_USERNAME


class Keyboard:
    def __init__(self, chat_username: str, battle_times: list[str]):
        self.__chat_username = chat_username
        self.__battle_times = battle_times
        (
            confirmation,
            admin_checking,
            channel_link,
            battle_mode,
            auction_mode,
            battles_times,
            auction,
            battle,
        ) = self.__get_markups()

        self.confirmation = InlineKeyboardMarkup(inline_keyboard=confirmation)
        self.admin_checking = InlineKeyboardMarkup(inline_keyboard=admin_checking)
        self.channel_link = InlineKeyboardMarkup(inline_keyboard=channel_link)
        self.battle_mode = InlineKeyboardMarkup(inline_keyboard=battle_mode)
        self.battles_times = battles_times.as_markup()
        self.auction_mode = InlineKeyboardMarkup(inline_keyboard=auction_mode)
        self.auction = InlineKeyboardMarkup(inline_keyboard=auction)
        self.battle = InlineKeyboardMarkup(inline_keyboard=battle)

    def __get_markups(self):
        confirmation_markup = [
            [
                InlineKeyboardButton(text="✅", callback_data="confirmed"),
                InlineKeyboardButton(text="❌", callback_data="cancelled"),
            ]
        ]

        admin_checking_markup = [
            [
                InlineKeyboardButton(text="✅", callback_data="accepted"),
                InlineKeyboardButton(text="❌", callback_data="not_accepted"),
            ]
        ]

        channel_link_markup = [
            [
                InlineKeyboardButton(
                    text="Подписаться", url=f"t.me/{self.__chat_username}"
                )
            ]
        ]

        battle_mode_markup = [
            [
                InlineKeyboardButton(text="📋", callback_data="get_bmembers"),
                InlineKeyboardButton(text="💰", callback_data="change_battle_prize"),
            ],
            [InlineKeyboardButton(text="💸", callback_data="to_auction")],
        ]

        battles_times_builder = InlineKeyboardBuilder()
        for bt in self.__battle_times:
            text = bt[:-3].replace("-", ":")
            battles_times_builder.button(text=text, callback_data=f"bmembers_{bt}")
        battles_times_builder.adjust(3)

        auction_mode_markup = [
            [
                InlineKeyboardButton(text="⚔️", callback_data="to_battle"),
                InlineKeyboardButton(text="💰", callback_data="change_auction_prize"),
            ]
        ]

        auction_markup = [
            [InlineKeyboardButton(text="Принять участие", callback_data="auction_join")]
        ]

        battle_markup = [
            [
                InlineKeyboardButton(
                    text="Принять участие",
                    url=f"https://t.me/{BOT_USERNAME}?start=None",
                )
            ]
        ]

        return (
            confirmation_markup,
            admin_checking_markup,
            channel_link_markup,
            battle_mode_markup,
            auction_mode_markup,
            battles_times_builder,
            auction_markup,
            battle_markup,
        )
