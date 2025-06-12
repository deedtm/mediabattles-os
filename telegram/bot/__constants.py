import json

with open("telegram/bot/templates.json", "r", encoding="utf8") as f:
    TEMPLATES: dict[str, str | list] = json.load(f)

CB_MSGS = TEMPLATES['callback_messages']
