import logging
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from config.telegram import CHANNEL_ID, TOKEN
from payments import payment
from battle.utils import get_nearest_contest, get_battle_members
from .__utils import get_member_data, get_user_data
from ..objects import kb, battle, admin, emojiid
from .__constants import TEMPLATES, CB_MSGS
from .admins_handlers import router
from ..utils import get_username
from .states_groups.auction import AuctionWait


@router.message(Command("start"))
async def start_handler(msg: Message):
    username = get_username(msg.from_user)
    logging.info(f"Got {msg.text} from {username}")

    nearest = get_nearest_contest(battle.TZ, battle.battles_times).strftime("%H:%M")
    try:
        await msg.answer(TEMPLATES["start"].format(nearest=nearest))
    except TelegramForbiddenError:
        logging.error(f"{username} is blocked")


@router.message(F.photo | F.video)
async def adding_handler(msg: Message):
    username = get_username(msg.from_user)
    logging.info(f"Got media from {username}")
    user = await msg.bot.get_chat_member(CHANNEL_ID, msg.from_user.id)

    if user.status == "left":
        await msg.answer(TEMPLATES["not_subscribed"], reply_markup=kb.channel_link)
        logging.info(f"{username} is not subcribed")
        return

    nearest = get_nearest_contest(battle.TZ, battle.battles_times)
    members = get_battle_members(nearest.strftime("%H-%M-%S"))

    if len(members) > 10 and str(msg.from_user.id) not in members:
        try:
            await msg.answer(
                TEMPLATES["members_full"].format(nearest=nearest.strftime("%H:%M"))
            )
        except TelegramForbiddenError:
            logging.error(f"{username} is blocked")
        logging.info(f"Unsuccess: The battle is full")
        return

    if msg.photo:
        media_id = msg.photo[0].file_id
        media_type = "фото"
        answer_method = msg.answer_photo
    else:
        media_id = msg.video.file_id
        media_type = "видео"
        answer_method = msg.answer_video

    try:
        await answer_method(
            media_id,
            caption=TEMPLATES["confirmation"].format(media=media_type),
            reply_markup=kb.confirmation,
        )
    except TelegramForbiddenError:
        logging.error(f"{username} is blocked")


@router.callback_query(F.data.in_(("confirmed", "cancelled")))
async def confirmation_cb(q: CallbackQuery):
    to_user_text = TEMPLATES[q.data]

    if q.data == "confirmed":
        member_data = get_member_data(q.from_user.id, q.message)
        media_data = member_data[q.from_user.id]
        user_data = get_user_data(q.from_user)

        request_id = emojiid.generate()
        to_admin_text = TEMPLATES["admin"]["checking"].format(
            request_id=request_id, **user_data
        )

        await admin.send_message(q.bot, to_admin_text, media_data)

    username = get_username(q.from_user)
    logging.info(f"{username} is {q.data} media")

    try:
        await q.message.edit_caption(q.inline_message_id, to_user_text)
    except TelegramForbiddenError:
        logging.error(f"{username} is blocked")


@router.callback_query(F.data == "auction_join")
async def auction_join_cb(q: CallbackQuery, state: FSMContext):
    user_id = q.from_user.id
    msg_text = TEMPLATES[q.data]
    try:
        cb_text = CB_MSGS[0]
        await q.bot.send_message(user_id, msg_text)
        bot_id = int(TOKEN.split(':')[0])
        key = StorageKey(bot_id, user_id, user_id)
        new_state = FSMContext(state.storage, key)
        await new_state.set_state(AuctionWait.value)
    except TelegramForbiddenError as err:
        error_str = err.__str__()
        cb_text = error_str
        if "can't initiate" in error_str:
            cb_text = CB_MSGS[1]
        elif "was blocked" in error_str:
            cb_text = CB_MSGS[2]
    await q.answer(cb_text)


@router.message(AuctionWait.value)
async def auction_payment(msg: Message, state: FSMContext):
    try:
        value = int(msg.text)
        url = payment.create(value, msg.from_user.id)
        template = TEMPLATES['auction_payment']
        text = template.format(url=url)
        await state.set_state()
    except ValueError:
        text = TEMPLATES['errors']['not_int']
    
    await msg.answer(text)
    