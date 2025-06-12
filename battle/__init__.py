import json
from os_utils import get_cwd_path
from datetime import timezone, datetime, timedelta
from .utils import get_nearest_contest, get_battle_members, save_battle_members

class Battle:
    def __init__(self, battles_times: list[datetime], time_format: str):
        self.TIME_FORMAT = time_format
        self.LIST_PATH = get_cwd_path('battle/list/')
        self.battles_times = battles_times
        self.TZ = timezone(timedelta(0, 0, 0, 0, 0, 3), 'МСК')
        self.__create_jsons()
    
    def add_member(self, member: dict[str, dict[str, str]]):
        result = 'added'
        prev_media = None
        nearest_battle_dt = get_nearest_contest(self.TZ, self.battles_times)
        battle = nearest_battle_dt.strftime(self.TIME_FORMAT)
        media = get_battle_members(battle)
        
        user_id = str(list(member.keys())[0])
        if user_id not in media:
            media.update(member)
        else:
            prev_media = media[user_id]
            media[user_id] == member[int(user_id)]
            result = 'updated'
        
        save_battle_members(battle, media)

        return result, prev_media
        
    def __create_jsons(self):
        for t in self.battles_times:
            fn = t.strftime(f'{self.TIME_FORMAT}.json')
            
            with open(self.LIST_PATH + fn, 'w') as f: 
                json.dump({}, f)
            