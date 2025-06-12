from typing import Optional
from aiogram.types import InputMediaPhoto, InputMediaVideo, User
from .constants import HYPERLINKF, USER_ID_LINKF, USERNAME_LINKF


def get_input_media(media_data: dict[str, str], caption: str | None = None):
    return (
        InputMediaPhoto(media=media_data["id"], caption=caption)
        if media_data["type"] == "photo"
        else InputMediaVideo(media=media_data["id"], caption=caption)
    )


def get_username(user: User):
    return "@" + user.username if user.username else user.id


def get_user_hyperlink(user: User, text: Optional[str] = None):
    link = (
        USERNAME_LINKF.format(user.username)
        if user.username
        else USER_ID_LINKF.format(user.id)
    )
    if text is None:
        text = user.full_name
    return HYPERLINKF.format(link, text)
