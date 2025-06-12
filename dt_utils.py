from datetime import datetime, timedelta

def string_to_time(string: str, format: str):
    return datetime.strptime(string, format).time()


def strings_to_times(strings: list[str], format: str):
    return [string_to_time(s, format) for s in strings]


def string_to_datetime(string: str, format: str):
    output = datetime.strptime(string, format)
    if output.year == 1900:
        output = datetime.combine(datetime.min, output.time())
    return output


def strings_to_datetimes(strings: list[str], format: str):
    return [string_to_datetime(s, format) for s in strings]


def prettify_seconds(seconds: int):    
    formatted = datetime(1, 1, 1, 0, 0, 0, 0) + timedelta(seconds=seconds)
    
    if formatted.hour != 0:
        format = "%H ч. %M мин." if formatted.minute != 0 else "%H ч."
        return formatted.strftime(format).lstrip('0')
    
    if formatted.minute != 0:
        return formatted.strftime("%M мин.").lstrip('0')
    
    return formatted.strftime("%S сек.").lstrip('0')
        