from datetime import datetime, timedelta

WEEKDAYS = ['月', '火', '水', '木', '金', '土', '日']

def get_day_label(offset=0):
    today = datetime.now() + timedelta(days=offset)
    weekday = WEEKDAYS[today.weekday()]
    return weekday

def get_period_from_slot(slot_value):
    try:
        return int(slot_value.replace('限', '').replace('時間目', ''))
    except:
        return None
