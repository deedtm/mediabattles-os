import json
import logging
from .. import posting_data_utils as posting_data
from datetime import datetime, timedelta, time, timezone
from math import ceil
from random import choice
from asyncio import sleep
from aiogram import Bot
from aiogram.types import Poll, ChatMemberMember
from aiogram.exceptions import TelegramForbiddenError
from battle.utils import get_nearest_contest
from payments.operations import get_biggest_payment

# from donation_api.utils import get_biggest_donater, save_donaters
from dt_utils import prettify_seconds
from .__utils import get_time_total_seconds
from ..utils import get_input_media, get_user_hyperlink
from ..effects import EffectsIDS
from ..bot.__utils import save_handled_requests
from ..objects import kb
from ..utils import get_user_hyperlink


class Poster:
    def __init__(
        self,
        bot: Bot,
        channel_id: int,
        bot_username: str,
        admins_ids: list[int],
        schedule: list[datetime],
        time_format: str,
        before_battle_time: time,
        rounds_interval: time,
        auction_rounds_num: int,
        auction_duration: time,
    ):
        self.bot = bot
        self.channel_id = channel_id
        self.bot_username = bot_username
        self.schedule = schedule
        self.admins_ids = admins_ids

        self.TIME_FORMAT = time_format

        self.AUCTION_ROUNDS = auction_rounds_num
        self.AUCTION_DURATION = auction_duration

        self.BEFORE_BATTLE_TIME = before_battle_time
        self.ROUNDS_INTERVAL = rounds_interval

        self.AUCTION_DURATION_SECONDS = get_time_total_seconds(self.AUCTION_DURATION)

        self.BEFORE_BATTLE_SECONDS = get_time_total_seconds(self.BEFORE_BATTLE_TIME)
        self.ROUNDS_INTERVAL_SECONDS = get_time_total_seconds(rounds_interval)

        self.TZ = timezone(timedelta(0, 0, 0, 0, 0, 3), "МСК")

        with open("telegram/channel/templates.json") as f:
            self.TEMPLATES = json.load(f)

        self.NUMBERS_EMOJIS = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

    async def start(self):
        logging.info(f"Starting {self.__class__.__name__}...")

        while True:
            send_time = get_nearest_contest(
                self.TZ, self.schedule
            ).time()  # (now + timedelta(minutes=1)).time()
            wait_for = await self.__get_wait_for_posting(send_time)
            logging.info(f"Sleeping for {wait_for / 3600:0.1f} hours before posting...")
            await sleep(wait_for)
            posting_mode = posting_data.get()["mode"]
            if posting_mode == "auction":
                wait_for_auction = self.BEFORE_BATTLE_SECONDS
                if wait_for < 0:
                    wait_for_auction += wait_for
                logging.info(
                    f"Sleeping for {wait_for_auction / 60:0.1f} minutes before posting..."
                )
                await sleep(wait_for_auction)

            if posting_mode == "battle":
                await self.__battle_wrapper(send_time.strftime(self.TIME_FORMAT))
            elif posting_mode == "auction":
                await self.__start_auction()
            else:
                logging.error(f"{posting_mode} is invalid value for mode. Skipping...")

    async def __get_wait_for_posting(self, send_time: time):
        now = datetime.now(self.TZ)

        if now.time() > send_time:
            tomorrow = datetime.combine(
                now.date() + timedelta(days=1), send_time, self.TZ
            )
            wait_for = (tomorrow - now).total_seconds()
        else:
            send_date = datetime.combine(now.date(), send_time, self.TZ)
            wait_for = (send_date - now).total_seconds()

        wait_for -= self.BEFORE_BATTLE_SECONDS
        return wait_for

    async def __start_auction(self):
        pretty_time = prettify_seconds(self.AUCTION_DURATION_SECONDS)

        auction_prize = posting_data.get()["auction_prize"]
        text = self.TEMPLATES["auction"]["start"].format(
            prize=auction_prize, time=pretty_time
        )
        auction_message = await self.bot.send_message(
            self.channel_id, text, reply_markup=kb.auction
        )

        user_id = await self.__start_auction_rounds()

        await self.bot.delete_message(self.channel_id, auction_message.message_id)
        await self.__send_auction_winner(user_id, auction_prize)

    async def __send_auction_winner(self, user_id: int, auction_prize: int):
        text = self.TEMPLATES["auction"]["finish"].format(prize=auction_prize)
        kwargs = {
            "chat_id": self.channel_id,
            "text": text,
        }
        await self.bot.send_message(**kwargs)

        if not user_id:
            return
        member = await self.bot.get_chat_member(self.channel_id, user_id)
        hyperlink = get_user_hyperlink(member.user)

        kwargs["text"] = self.TEMPLATES["auction"]["admin"].format(
            prize=auction_prize, user=hyperlink
        )
        for admin_id in self.admins_ids:
            kwargs["chat_id"] = admin_id
            await self.bot.send_message(**kwargs)

    async def __start_auction_rounds(self):
        auc_start = datetime.now(self.TZ)
        rounds_interval = (self.AUCTION_DURATION_SECONDS - 120) / self.AUCTION_ROUNDS
        round = 0

        await sleep(60)
        while round != self.AUCTION_ROUNDS:
            round += 1
            msg, user_id = await self.__send_biggest_payment(
                round, rounds_interval, auc_start
            )
            await sleep(rounds_interval)
            if msg:
                await self.bot.delete_message(self.channel_id, msg.message_id)

        # пост за минуту до конца
        msg, user_id = await self.__send_biggest_payment(
            round + 1, rounds_interval, auc_start
        )
        await sleep(60)
        if msg:
            await self.bot.delete_message(self.channel_id, msg.message_id)
        return user_id

    async def __send_biggest_payment(
        self, round: int, rounds_interval: int, auction_start_dt: datetime
    ):
        payment = get_biggest_payment(auction_start_dt)
        if payment is None:
            return None, None
        amount, user_id = payment
        amount = ceil(amount)

        left_seconds = self.AUCTION_DURATION_SECONDS - (rounds_interval * round) + 60
        left_time = prettify_seconds(left_seconds)

        text_kwargs = {"money": amount, "time": left_time}
        template = self.TEMPLATES["auction"]["round"]
        text = template.format(**text_kwargs)
        msg = await self.bot.send_message(
            self.channel_id, text, reply_markup=kb.auction
        )

        return msg, user_id

    async def __battle_wrapper(self, battle_time: str):
        save_handled_requests({})
        prize = posting_data.get()["battle_prize"]
        bb_msg_id = await self.__send_before_battle_msg(prize)

        logging.info(f"Sleeping for {self.BEFORE_BATTLE_SECONDS / 60:0.1f} minutes...")
        await sleep(self.BEFORE_BATTLE_SECONDS)

        await self.bot.delete_message(self.channel_id, bb_msg_id)

        logging.info("Starting battle")
        is_sent, winner = await self.__start_battle(battle_time, prize)

        if is_sent:
            winner_id, winner_media = list(winner.items())[0]
            await self.__send_battle_winner(int(winner_id), winner_media, prize)
        else:
            logging.info("Not enough members for contest")

        with open(f"battle/list/{battle_time}.json", "w") as f:
            json.dump({}, f)

    async def __send_before_battle_msg(self, prize: int):
        pretty_time = prettify_seconds(self.BEFORE_BATTLE_SECONDS)
        before_battle_text = self.TEMPLATES["battle"]["before"].format(
            prize=prize, time=pretty_time, bot_username=self.bot_username
        )

        before_battle_msg = await self.bot.send_message(
            chat_id=self.channel_id,
            text=before_battle_text,
            disable_web_page_preview=True,
            reply_markup=kb.battle,
        )
        logging.info("Sent before battle message")

        return before_battle_msg.message_id

    async def __send_battle_winner(
        self, winner_id: int, winner_media: dict[str, str], prize: int
    ):
        send_method = (
            self.bot.send_photo
            if winner_media["type"] == "photo"
            else self.bot.send_video
        )

        caption = self.TEMPLATES["winner"]["channel"]
        kwargs = {
            "chat_id": self.channel_id,
            "caption": caption,
            winner_media["type"]: winner_media["id"],
        }
        await send_method(**kwargs)

        try:
            kwargs.update({"message_effect_id": EffectsIDS.TADA})
            caption = self.TEMPLATES["winner"]["user"]
            kwargs["chat_id"], kwargs["caption"] = winner_id, caption
            await send_method(**kwargs)

            winner_member = await self.bot.get_chat_member(self.channel_id, winner_id)
            winner_link = get_user_hyperlink(winner_member.user)
        except TelegramForbiddenError:
            logging.info(f"{winner_id} is blocked")
            winner_link = "пользователь заблокирован ☠️"

        kwargs["caption"] = self.TEMPLATES["winner"]["admin"].format(
            winner=winner_link, prize=prize
        )
        for admin_id in self.admins_ids:
            kwargs["chat_id"] = admin_id
            await send_method(**kwargs)

    async def __start_battle(self, time: str, prize: int):
        with open(f"battle/list/{time}.json") as f:
            members: dict[str, dict[str, str]] = json.load(f)

        if len(members) < 2:
            return False, {}

        round_num = 0
        kicked_nums = []
        while len(members) != 1:
            round_num += 1
            poll_msg = await self.__send_round(round_num, members, prize, kicked_nums)
            await sleep(self.ROUNDS_INTERVAL_SECONDS)

            poll = await self.bot.stop_poll(self.channel_id, poll_msg.message_id)
            members, kicked_nums = self.__get_winners(poll, members)

        return True, members

    async def __send_round(
        self,
        round_num: int,
        members: dict[str, dict[str, str]],
        prize: int,
        kicked_nums: list[str] | None = None,
    ):
        media_datas = list(members.values())

        caption = self.__get_caption(round_num, prize, kicked_nums)
        medias = [get_input_media(media_datas[0], caption)]

        for media_data in media_datas[1:]:
            media = get_input_media(media_data)
            medias.append(media)

        await self.bot.send_media_group(self.channel_id, medias)
        return await self.__send_poll(len(members))

    async def __send_poll(self, members_amount):
        options = [str(i) for i in range(1, members_amount + 1)]
        question = choice(self.TEMPLATES["poll"]["questions"])
        return await self.bot.send_poll(
            self.channel_id,
            question,
            options,
            is_anonymous=True,
        )

    def __get_winners(self, poll: Poll, members: dict[str, dict[str, str]]):
        members_items = list(members.items())
        votes = {}
        kicked_nums = []

        for option in poll.options:
            if option.voter_count == 0:
                kicked_nums.append(option.text)
                continue
            votes.setdefault(option.text, option.voter_count)

        winners = {}
        winners_amount = self.__get_winners_amount(len(members_items))
        if winners_amount > len(votes):
            winners_amount = len(votes)

        votes_values = list(votes.values())
        votes_keys = list(votes.keys())

        for _ in range(winners_amount):
            if not votes_values:
                break
            maximum = max(votes_values)
            for _ in range(votes_values.count(maximum)):
                maximum_ind = votes_values.index(maximum)
                maximum_key = votes_keys[maximum_ind]

                votes.pop(maximum_key)
                votes_keys.pop(maximum_ind)
                votes_values.pop(maximum_ind)

                winners.setdefault(*members_items[int(maximum_key) - 1])
        kicked_nums.extend(list(votes.keys()))

        if not winners:
            winners = members
            kicked_nums = []

        return winners, kicked_nums

    def __get_winners_amount(self, members_amount: int):
        if members_amount % 2 == 0:
            return members_amount // 2
        else:
            return (members_amount + 1) // 2

    def __get_caption(
        self, round_num: int, prize: int, kicked_nums: list[str] | None = None
    ):
        emoji_num = self.__number_to_emoji(round_num)
        next_round_time = prettify_seconds(self.ROUNDS_INTERVAL_SECONDS)
        kwargs = {
            "round_num": emoji_num,
            "prize": prize,
            "next_round_time": next_round_time,
        }
        template = "start"

        if round_num != 1:
            template = "round"
            kwargs.setdefault("kicked_nums", ", ".join(kicked_nums))

        return self.TEMPLATES["battle"][template].format(**kwargs)

    def __number_to_emoji(self, number: int):
        number = str(number)
        return "".join([self.NUMBERS_EMOJIS[int(digit)] for digit in number])
