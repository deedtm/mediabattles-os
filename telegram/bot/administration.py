import logging
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from ..keyboard import Keyboard
from ..effects import EffectsIDS


class Administration:
    def __init__(self, kb: Keyboard, admins_ids: list[int]):
        self.admins_ids = admins_ids
        self.kb = kb

    async def send_message(
        self, bot: Bot, text: str, media: dict[str, str] | None = None
    ):
        if not media:
            send_method = bot.send_message
            kwargs = {"text": text}
        else:
            send_method = bot.send_photo if media["type"] == "photo" else bot.send_video
            kwargs = {"caption": text, media["type"]: media["id"]}

        for admin_id in self.admins_ids:
            try:
                await send_method(
                    chat_id=admin_id, reply_markup=self.kb.admin_checking, **kwargs
                )
            except TelegramBadRequest:
                continue

    async def send_check_result(
        self,
        send_method,
        user_id: int,
        media_kwargs: dict,
        result: int,
        template: str | None = None,
        media_type: str | None = None,
        admin_message: str | None = None,
        is_new: bool = True
    ):
        if not is_new and template is None and media_type is None:
            raise AttributeError('if media is not new, template and media_type must be filled')
        effect = EffectsIDS.LIKE if result == 1 else EffectsIDS.DISLIKE
        kwargs = {'chat_id': user_id, "message_effect_id": effect}
        
        if is_new:
            format_kwargs = {'media_type': media_type}
            if admin_message is not None:
                format_kwargs.setdefault("message", admin_message)
            kwargs.setdefault('caption', template.format(**format_kwargs))
        
        try: await send_method(**kwargs, **media_kwargs)
        except TelegramForbiddenError: logging.error(f"{user_id} blocked the bot")
        