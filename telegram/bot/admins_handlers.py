import logging
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime
from .. import posting_data_utils as posting_data
from ..utils import get_input_media, get_user_hyperlink, get_username
from .form import Form
from battle.utils import get_battle_members
from ..objects import battle, router, admin, kb
from .__constants import TEMPLATES
from .__utils import (
    get_member_data,
    get_admin_answer,
    get_request_id,
    add_handled_request,
    get_handled_requests,
    save_handled_requests,
    get_media_data,
)
from payments.operations import get_biggest_payment


@router.message(Command("test_payment"), F.from_user.id.in_(admin.admins_ids))
async def test_payment_handler(msg: Message):
    get_biggest_payment(datetime(2024, 8, 1))
    await msg.answer("Payment test", reply_markup=kb.auction)


@router.message(Command("panel"), F.from_user.id.in_(admin.admins_ids))
async def mode_handler(msg: Message):
    username = get_username(msg.from_user)
    logging.info(f"Got {msg.text} from {username}")

    pdata = posting_data.get()
    posting_mode = pdata["mode"]
    prize = pdata[posting_mode + '_prize']

    template = TEMPLATES["admin"][f"mode_{posting_mode}"]
    text = template.format(prize=prize)            
    reply_markup = kb.battle_mode if posting_mode == "battle" else kb.auction_mode

    await msg.answer(text, reply_markup=reply_markup)


@router.callback_query(F.data.in_(("to_battle", "to_auction")))
async def change_mode_cb(q: CallbackQuery):
    pdata = posting_data.get()
    posting_mode = q.data[3:]
    pdata["mode"] = posting_mode
    posting_data.update(pdata)

    text = TEMPLATES["admin"][f"mode_{posting_mode}"]
    if posting_mode == "battle":
        reply_markup = kb.battle_mode
    else:
        auction_prize = pdata["auction_prize"]
        reply_markup = kb.auction_mode
        text = text.format(prize=auction_prize)

    await q.message.edit_text(text, reply_markup=reply_markup)

    username = get_username(q.from_user)
    logging.info(f"{username} changed posting mode to {posting_mode}")


@router.callback_query(F.data == "get_bmembers")
async def battles_times_cb(q: CallbackQuery):
    text = TEMPLATES["admin"]["battles_times"]
    await q.message.edit_text(text, reply_markup=kb.battles_times)


@router.callback_query(F.data.startswith("bmembers_"))
async def battle_members_cb(q: CallbackQuery):
    await q.answer(text="💨💨💨 VINE BOOM EFFECT 💨💨💨")

    battle_time = q.data.split("_")[-1]
    user_time = battle_time[:-3].replace("-", ":")
    members = get_battle_members(battle_time)

    if not members:
        text = TEMPLATES["errors"]["empty_members"].format(time=user_time)
        try:
            await q.message.edit_text(text, reply_markup=kb.battles_times)
        except TelegramBadRequest:
            pass
        return

    user_links = []
    medias = []
    for user_id, media_data in members.items():
        chat = await q.bot.get_chat(int(user_id))
        user_link = get_user_hyperlink(chat)
        user_links.append(user_link)
        medias.append(get_input_media(media_data))

    template = TEMPLATES["admin"]["battle_members"]
    text = template.format(time=user_time, members="\n".join(user_links))
    medias[0].caption = text

    await q.bot.send_media_group(q.message.chat.id, medias)


@router.callback_query(F.data.contains("change_"))
async def change_battle_prize_cb(q: CallbackQuery, state: FSMContext):
    await q.answer(text="VINE BOOM EFFECT")
    event = q.data.split('_')[1]
    await state.set_state(Form.prize)
    await state.update_data(event=event)
    
    text = TEMPLATES['admin']['waiting_prize']
    await q.bot.send_message(q.from_user.id, text)
    

@router.message(Form.prize)
async def process_prize(msg: Message, state: FSMContext):
    try:
        data = await state.get_data()
        event = data['event']
        
        prize = int(msg.text)
        pdata = posting_data.get()
        pdata[event + "_prize"] = prize
        posting_data.update(pdata)

        text = TEMPLATES["admin"]["got_prize"].format(prize=prize)
        await msg.answer(text)

        username = get_username(msg.from_user)
        logging.info(f"{username} changed {event} prize to {prize}")
    except ValueError:
        text = TEMPLATES["errors"]["prize_not_number"]
        await msg.answer(text)

    await state.set_state()


@router.callback_query(F.data.in_(("accepted", "not_accepted")))
async def accepting_cb(q: CallbackQuery, state: FSMContext):
    req_id = get_request_id(q.message.caption)
    handled_reqs = get_handled_requests()

    if req_id in handled_reqs:
        req_msg = handled_reqs[req_id]
        admin_answer = TEMPLATES["admin"]["already_handled"].format(message=req_msg)
        await q.message.edit_caption(q.inline_message_id, admin_answer)
        return

    emoji, decision = TEMPLATES["admin"][q.data]
    admin_answer, user_id = get_admin_answer(q.message.caption, emoji, decision)
    await q.message.edit_caption(q.inline_message_id, admin_answer)

    media_data = get_media_data(q)
    await state.update_data(user_id=user_id, req_id=req_id, media_data=media_data)

    logging.info(
        "@{admin} {decision} media from {user} — {req_id}".format(
            admin=q.from_user.username,
            decision=q.data.replace("_", " "),
            user=admin_answer.split("\n\n")[1][3:],
            req_id=req_id,
        )
    )

    add_handled_request(req_id, admin_answer.split("\n")[0])

    if q.data == "not_accepted":
        await state.set_state(Form.admin_msg)
        await q.bot.send_message(q.message.chat.id, TEMPLATES["admin"]["waiting_msg"])
        return

    member_data = get_member_data(user_id, q.message)
    result, prev_media = battle.add_member(member_data)

    media_type = media_data[0]
    media_kwargs = media_data[1]
    template = TEMPLATES["accepted"][result]
    caption = None
    kwargs = {}

    if result == "added":
        send_method = media_data[2]
        kwargs.update({"template": template, "media_type": media_type, "is_new": True})
    else:
        send_method = q.bot.send_media_group

        media_items = list(media_kwargs.items())[0]
        media_input = get_input_media({"type": media_items[0], "id": media_items[1]})

        caption = template.format(media_type=media_type)
        prev_media_input = get_input_media(prev_media, caption)

        media_kwargs = {"media": [prev_media_input, media_input]}
        kwargs.update({"template": template, "is_new": False})

    await admin.send_check_result(send_method, user_id, media_kwargs, 1, **kwargs)


@router.message(Form.admin_msg)
async def process_admin_msg(msg: Message, state: FSMContext):
    await state.update_data(admin_msg=msg.text)
    await msg.answer(TEMPLATES["admin"]["sent_msg"])

    logging.info(f"Reason: {msg.text}")

    data = await state.get_data()
    user_id: int = data.get("user_id")
    req_id: str = data.get("req_id")
    media_data: tuple = data.get("media_data")

    reqs = get_handled_requests()
    reqs[req_id] += f"\n\n✉️  {msg.text}"
    save_handled_requests(reqs)

    media_type = media_data[0]
    media_kwargs = media_data[1]
    send_method = media_data[2]
    template = TEMPLATES["not_accepted"]
    await admin.send_check_result(
        send_method,
        user_id,
        media_kwargs,
        0,
        template,
        media_type,
        admin_message=msg.text,
    )

    await state.set_state()
