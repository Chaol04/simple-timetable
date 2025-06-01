import os
import json
import random
from datetime import datetime

DATA_DIR = "data"
BASE_URL = "https://smpl-tmbl.onrender.com/timetable/"  # 60字以内の短縮URLベース

os.makedirs(DATA_DIR, exist_ok=True)

def generate_uid():
    return ''.join(random.choices('0123456789', k=6))

def get_user_uid(user_id):
    uid_path = os.path.join(DATA_DIR, f"{user_id}.uid")
    if os.path.exists(uid_path):
        return open(uid_path).read().strip()
    else:
        uid = generate_uid()
        with open(uid_path, 'w') as f:
            f.write(uid)
        return uid

def get_timetable(uid):
    path = os.path.join(DATA_DIR, f"{uid}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def save_timetable(uid, timetable):
    path = os.path.join(DATA_DIR, f"{uid}.json")
    with open(path, 'w') as f:
        json.dump(timetable, f)
