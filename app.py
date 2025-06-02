from flask import Flask, request
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_intent_name
from datetime import datetime, timedelta

app = Flask(__name__)
sb = SkillBuilder()

# 時間割データ（月〜土、1〜5限）
timetable = {
    "月曜日": ["自己発見と大学生活", "コンピュータ概論", "", "", ""],
    "火曜日": ["", "コンピュータのための数学", "批判的思考と論理的表現", "大学数学の基礎演習", ""],
    "水曜日": ["プログラミング演習A", "プログラミング演習A", "", "", "中級英語コミュニケーション"],
    "木曜日": ["", "中級英語TOEIC", "微分積分", "情報理工学概論", ""],
    "金曜日": ["倫理学", "線形代数", "人工知能の進化と活用", "", ""],
    "土曜日": ["", "", "電子回路", "電子回路", ""]
}
weekdays = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]

def get_japanese_weekday(date):
    return weekdays[date.weekday()]

# Intent: スキル起動時の応答
class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.object_type == "LaunchRequest"

    def handle(self, handler_input):
        speech = "シンプル時間割へようこそ。今日の時間割を聞きますか？"
        return handler_input.response_builder.speak(speech).set_should_end_session(False).response

# Intent: 今日の時間割
class GetTodayTimetableIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetTodayTimetableIntent")(handler_input)

    def handle(self, handler_input):
        today = get_japanese_weekday(datetime.now())
        schedule = timetable.get(today, [])
        spoken = "、".join(filter(None, schedule))
        speech = f"{today}の時間割は、{spoken}です。" if spoken else f"{today}の時間割は登録されていません。"
        return handler_input.response_builder.speak(speech).response

# Intent: 明日の時間割
class GetTomorrowTimetableIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetTomorrowTimetableIntent")(handler_input)

    def handle(self, handler_input):
        tomorrow = get_japanese_weekday(datetime.now() + timedelta(days=1))
        schedule = timetable.get(tomorrow, [])
        spoken = "、".join(filter(None, schedule))
        speech = f"{tomorrow}の時間割は、{spoken}です。" if spoken else f"{tomorrow}の時間割は登録されていません。"
        return handler_input.response_builder.speak(speech).response

# Intent: 任意曜日の時間割
class GetDayTimetableIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetDayTimetableIntent")(handler_input)

    def handle(self, handler_input):
        day = handler_input.request_envelope.request.intent.slots["day"].value
        schedule = timetable.get(day, [])
        spoken = "、".join(filter(None, schedule))
        speech = f"{day}の時間割は、{spoken}です。" if spoken else f"{day}の時間割は登録されていません。"
        return handler_input.response_builder.speak(speech).response

# Intent: 任意曜日 + 限目
class GetSpecificPeriodIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetSpecificPeriodIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        day = slots["day"].value
        period = int(slots["period"].value) - 1
        schedule = timetable.get(day, [])
        if 0 <= period < len(schedule):
            subject = schedule[period] or "登録されていません"
            speech = f"{day}の{period + 1}限は{subject}です。"
        else:
            speech = f"{day}の{period + 1}限は存在しません。"
        return handler_input.response_builder.speak(speech).response

# Intent: 今日のX限
class GetTodayPeriodIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetTodayPeriodIntent")(handler_input)

    def handle(self, handler_input):
        period = int(handler_input.request_envelope.request.intent.slots["period"].value) - 1
        today = get_japanese_weekday(datetime.now())
        schedule = timetable.get(today, [])
        if 0 <= period < len(schedule):
            subject = schedule[period] or "登録されていません"
            speech = f"今日の{period + 1}限は{subject}です。"
        else:
            speech = f"今日の{period + 1}限は存在しません。"
        return handler_input.response_builder.speak(speech).response

# Intent: 明日のX限
class GetTomorrowPeriodIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetTomorrowPeriodIntent")(handler_input)

    def handle(self, handler_input):
        period = int(handler_input.request_envelope.request.intent.slots["period"].value) - 1
        tomorrow = get_japanese_weekday(datetime.now() + timedelta(days=1))
        schedule = timetable.get(tomorrow, [])
        if 0 <= period < len(schedule):
            subject = schedule[period] or "登録されていません"
            speech = f"明日の{period + 1}限は{subject}です。"
        else:
            speech = f"明日の{period + 1}限は存在しません。"
        return handler_input.response_builder.speak(speech).response

# 例外処理ハンドラ
class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print(f"❌ 例外発生: {exception}")
        return handler_input.response_builder.speak("エラーが発生しました。").response

# ハンドラ登録
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetTodayTimetableIntentHandler())
sb.add_request_handler(GetTomorrowTimetableIntentHandler())
sb.add_request_handler(GetDayTimetableIntentHandler())
sb.add_request_handler(GetSpecificPeriodIntentHandler())
sb.add_request_handler(GetTodayPeriodIntentHandler())
sb.add_request_handler(GetTomorrowPeriodIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

# Flask ルーティング
@app.route("/", methods=["POST"])
def invoke():
    data = request.get_json(force=True)
    print("🔵 Alexaからのリクエスト内容：", data)
    return sb.lambda_handler()(data, None)
