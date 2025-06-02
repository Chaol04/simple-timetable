from flask import Flask, request
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_intent_name
from datetime import datetime, timedelta

app = Flask(__name__)
sb = SkillBuilder()

# 🗓 時間割データ（1〜5限、月〜土）
timetable = {
    "月曜日": ["数学", "英語", "理科", "社会", "体育"],
    "火曜日": ["国語", "美術", "英語", "数学", "音楽"],
    "水曜日": ["理科", "体育", "国語", "英語", "家庭科"],
    "木曜日": ["社会", "理科", "英語", "技術", "数学"],
    "金曜日": ["国語", "数学", "社会", "体育", "英語"],
    "土曜日": ["保健", "道徳", "自習", "英会話", "総合"]
}

# 曜日リスト（月〜土対応）
weekdays = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]

def get_japanese_weekday(date):
    return weekdays[date.weekday()]

# Intent Handlers（省略せずすべて対応）

class GetTodayTimetableHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetTodayTimetableIntent")(handler_input)

    def handle(self, handler_input):
        today = get_japanese_weekday(datetime.now())
        schedule = timetable.get(today, [])
        if schedule:
            speech = f"{today}の時間割は、" + "、".join(schedule) + "です。"
        else:
            speech = f"{today}の時間割は登録されていません。"
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

class GetTomorrowTimetableHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetTomorrowTimetableIntent")(handler_input)

    def handle(self, handler_input):
        tomorrow = get_japanese_weekday(datetime.now() + timedelta(days=1))
        schedule = timetable.get(tomorrow, [])
        if schedule:
            speech = f"{tomorrow}の時間割は、" + "、".join(schedule) + "です。"
        else:
            speech = f"{tomorrow}の時間割は登録されていません。"
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

class GetDayTimetableHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetDayTimetableIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        day = slots["day"].value
        schedule = timetable.get(day, [])
        if schedule:
            speech = f"{day}の時間割は、" + "、".join(schedule) + "です。"
        else:
            speech = f"{day}の時間割は登録されていません。"
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

class GetSpecificPeriodHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetSpecificPeriodIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        day = slots["day"].value
        period = int(slots["period"].value) - 1
        schedule = timetable.get(day, [])
        if 0 <= period < len(schedule):
            speech = f"{day}の{period + 1}限は{schedule[period]}です。"
        else:
            speech = f"{day}の{period + 1}限は登録されていません。"
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

class GetTodayPeriodHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetTodayPeriodIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        period = int(slots["period"].value) - 1
        today = get_japanese_weekday(datetime.now())
        schedule = timetable.get(today, [])
        if 0 <= period < len(schedule):
            speech = f"今日の{period + 1}限は{schedule[period]}です。"
        else:
            speech = f"今日の{period + 1}限は登録されていません。"
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

class GetTomorrowPeriodHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetTomorrowPeriodIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        period = int(slots["period"].value) - 1
        tomorrow = get_japanese_weekday(datetime.now() + timedelta(days=1))
        schedule = timetable.get(tomorrow, [])
        if 0 <= period < len(schedule):
            speech = f"明日の{period + 1}限は{schedule[period]}です。"
        else:
            speech = f"明日の{period + 1}限は登録されていません。"
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

# 登録
sb.add_request_handler(GetTodayTimetableHandler())
sb.add_request_handler(GetTomorrowTimetableHandler())
sb.add_request_handler(GetDayTimetableHandler())
sb.add_request_handler(GetSpecificPeriodHandler())
sb.add_request_handler(GetTodayPeriodHandler())
sb.add_request_handler(GetTomorrowPeriodHandler())

skill_handler = WebserviceSkillHandler(skill=sb.create())

@app.route("/", methods=["POST"])
def invoke():
    return skill_handler.verify_request_and_dispatch(request)
