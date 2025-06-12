import json
from os_utils import get_cwd_path

POSTING_DATA_PATH = get_cwd_path('telegram/posting_data.json')


def json_wrapper(open_mode='r'):
    def decorator(func):
        def wrapper(*args, **kwargs):
            with open(POSTING_DATA_PATH, open_mode) as f:
                return func(fp=f, *args, **kwargs)
        return wrapper
    return decorator


@json_wrapper()
def get(*, fp: str | bytes | None = None) -> dict[str, str]:
    return json.load(fp)
    
    
@json_wrapper('w')
def update(data: dict[str, str], *, fp: str | bytes | None = None):
    json.dump(data, fp, indent=4, ensure_ascii=False)

