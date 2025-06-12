import json

def get_donaters() -> dict[str, dict[str, int | str]]:
    with open('donation_api/donaters.json') as f:
        return json.load(f)


def save_donaters(donaters: dict):
    with open('donation_api/donaters.json', 'w') as f:
        json.dump(donaters, f, ensure_ascii=False, indent=4)


def get_biggest_donater():
    donaters = get_donaters()
    m = 0
    biggest = None
    
    for donater, data in donaters.items():
        if data['amount'] > m:
            m = data['amount']
            biggest = {"name": donater, "money": data['amount'], "message": data['message']}
    
    return biggest
