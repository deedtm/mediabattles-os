import json
from random import choice
from os_utils import get_cwd_path

class EmojiID:
    def __init__(self, id_length: int):
        path = get_cwd_path('emoji_identificator/emojis.json')
        with open(path) as f:
            emojis: list[str] = json.load(f)
        self.emojis = emojis
        self.length = id_length
        
    def generate(self, id_length: int | None = None):
        length = id_length if id_length else self.length
        return ''.join([choice(self.emojis) for _ in range(length)])
    