from datetime import time


def get_time_total_seconds(t: time):
    return (t.hour * 3600) + (t.minute * 60) + t.second
