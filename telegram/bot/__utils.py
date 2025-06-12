import json
from aiogram.types import Message, User, CallbackQuery


def get_member_data(from_user_id: int, message: Message):
    if message.photo:
        media_id = message.photo[0].file_id
        media_data = {"type": "photo", "id": media_id}
    else:
        media_id = message.video.file_id
        media_data = {"type": "video", "id": media_id}
    return {from_user_id: media_data}


def get_user_data(user: User):
    return {
        "first_name": user.first_name,
        "last_name": ' ' + user.last_name if user.last_name else '',
        "username": '@' + user.username + ' ' if user.username else '',
        "id": f"({user.id})" if user.username else user.id
        }


def get_request_id(msg_text: str):
    return msg_text.split('\n')[-1]


def get_admin_answer(message_text: str, emoji: str, decision: str):
    splitted_text = message_text.split('\n\n')
    splitted_text[0] = emoji + splitted_text[0][1:] + decision
    admin_answer = '\n\n'.join(splitted_text)
    
    user_info = splitted_text[1]
    if '(' not in user_info:
        user_id = int(user_info.split()[-1])
    else:
        user_id_start_ind = user_info.find('(') + 1
        user_id = int(user_info[user_id_start_ind:-1])
    
    return admin_answer, user_id    


def add_handled_request(req_id: str, message: str):
    handled_requests = get_handled_requests()        
    handled_requests.setdefault(req_id, message)
    save_handled_requests(handled_requests)


def get_handled_requests():
    with open('telegram/bot/handled_requests.json') as f:
        handled_requests: dict[str, str] = json.load(f)
    return handled_requests


def save_handled_requests(data: dict[str, str]):
    with open('telegram/bot/handled_requests.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
        
def get_media_data(q: CallbackQuery):
    if q.message.photo:
        type = "фото"
        kwargs = {'photo': q.message.photo[0].file_id}
        send_method = q.bot.send_photo
    else:
        type = "видео"
        kwargs = {'video': q.message.video.file_id}
        send_method = q.bot.send_video
        
    return type, kwargs, send_method
