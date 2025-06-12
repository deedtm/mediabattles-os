import json
from datetime import datetime
from . import client
from .constants import BASE_PATH, OPERATIONS_PATH, OPERATIONS_TYPE
from yoomoney import Operation


# def get_local():
#     with open(OPERATIONS_PATH) as f:
#         return json.load(f)


# def save_local(data):
#     with open(OPERATIONS_PATH, 'w') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)


# def add_local(op: Operation):
#     history = get_local()
#     history.append(op.__dict__)
#     save_local(history)


# def get_history(from_date: datetime):
#     h = client.operation_history(OPERATIONS_TYPE, from_date)
#     for o in h.operations:
#         print(o)


def get_biggest_payment(from_date: datetime):
    history = client.operation_history(OPERATIONS_TYPE, from_date=from_date)
    biggest, user_id = 0, 0
    for o in history.operations:
        if o.amount > biggest:
            try: user_id = int(o.label)
            except ValueError: continue
            biggest = o.amount
    if biggest == 0:
        return None
    return biggest, user_id
