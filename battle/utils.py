from datetime import datetime, timezone
import json


def get_nearest_contest(tz: timezone, battles_times: list[datetime]) -> datetime:
    current_time = datetime.now(tz).time()
    current_time_dt = datetime.combine(datetime.min, current_time)
    
    deltas = []
    times = []
    for t in battles_times:
        delta = t - current_time_dt
        if delta.total_seconds() < 0: continue
        deltas.append(delta)
        times.append(t)
        
    if not deltas:
        deltas = battles_times
        times = battles_times
    nearest_ind = deltas.index(min(deltas))
    nearest = times[nearest_ind]
    
    return nearest


def get_battle_members(battle_time: str):
    with open(f'battle/list/{battle_time}.json') as f:
        members: dict[str, dict[str, str]] = json.load(f)
    return members


def save_battle_members(battle_time: str, data: dict):
    with open(f'battle/list/{battle_time}.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
            