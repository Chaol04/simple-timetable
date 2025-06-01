from flask import Flask, request, render_template_string
from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard
from timetable_data import get_user_uid, get_timetable, save_timetable
from utils import get_day_label, get_period_from_slot

app = Flask(__name__)

# --- Alexaスキル部分 ---

sb = SkillBuilder()

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech = "シンプル時間割へようこそ。今日の時間割は？などと聞いてください。"
        return handler_input.response_builder.speak(speech).set_should_end_session(False).response

class TimetableQueryIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("TimetableQueryIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        user_id = handler_input.request_envelope.context.system.user.user_id
        uid = get_user_uid(user_id)
        timetable = get_timetable(uid)

        day = slots["day"].value if "day" in slots and slots["day"].value else None
        relative_day = slots.get("relative_day", {}).value if "relative_day" in slots else None
        period_slot = slots["period"].value if "period" in slots and slots["period"].value else None

        if not day:
            if relative_day == "明日":
                day = get_day_label(1)
            elif relative_day == "明後日":
                day = get_day_label(2)
            else:
                day = get_day_label(0)

        period = get_period_from_slot(period_slot) if period_slot else None
        day_key = day[:1]

        if day_key not in timetable:
            speech = f"{day}の時間割は登録されていません。"
        elif period:
            subject = timetable[day_key].get(str(period), "登録されていません")
            speech = f"{day}の{period}限は{subject}です。"
        else:
            periods = timetable[day_key]
            if periods:
                subject_list = [f"{k}限は{v}" for k, v in sorted(periods.items(), key=lambda x: int(x[0]))]
                speech = f"{day}の時間割は、" + "、".join(subject_list) + "です。"
            else:
                speech = f"{day}の時間割は登録されていません。"

        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

class SetTimetableIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SetTimetableIntent")(handler_input)

    def handle(self, handler_input):
        user_id = handler_input.request_envelope.context.system.user.user_id
        uid = get_user_uid(user_id)
        url = f"https://simple-timetable.onrender.com/timetable/{uid}"
        speech = "以下のリンクから時間割を登録または変更してください。"
        card_text = f"時間割登録はこちら\n{url}"
        return handler_input.response_builder.speak(speech).set_card(
            SimpleCard("時間割の登録・変更", card_text)
        ).set_should_end_session(True).response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speech = "今日の時間割は？や、火曜日の4限は？などと聞いてください。"
        return handler_input.response_builder.speak(speech).set_should_end_session(False).response

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(TimetableQueryIntentHandler())
sb.add_request_handler(SetTimetableIntentHandler())
sb.add_request_handler(HelpIntentHandler())

skill_handler = WebserviceSkillHandler(skill=sb.create())

# --- Webフォーム部分 ---

WEEKDAYS_FULL = ['月', '火', '水', '木', '金', '土']

FORM_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>時間割登録 - {{ uid }}</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 600px; margin: 30px auto; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
    input[type=text] { width: 90%; }
    .message { color: green; margin-bottom: 15px; }
  </style>
</head>
<body>
  <h2>時間割登録・変更（UID: {{ uid }})</h2>
  {% if message %}
    <p class="message">{{ message }}</p>
  {% endif %}
  <form method="post">
    <table>
      <tr>
        <th>曜日 / 時限</th>
        {% for period in range(1,7) %}
          <th>{{ period }}限</th>
        {% endfor %}
      </tr>
      {% for day in weekdays %}
        <tr>
          <th>{{ day }}</th>
          {% for period in range(1,7) %}
            <td><input type="text" name="{{ day }}_{{ period }}" value="{{ timetable.get(day, {}).get(period|string, '') }}"></td>
          {% endfor %}
        </tr>
      {% endfor %}
    </table>
    <br>
    <button type="submit">保存</button>
  </form>
</body>
</html>
"""

@app.route('/timetable/<uid>', methods=['GET', 'POST'])
def timetable_form(uid):
    message = ""
    timetable = get_timetable(uid)

    if request.method == 'POST':
        new_tt = {}
        for day in WEEKDAYS_FULL:
            new_tt[day] = {}
            for period in range(1,7):
                key = f"{day}_{period}"
                subject = request.form.get(key, '').strip()
                if subject:
                    new_tt[day][str(period)] = subject
        save_timetable(uid, new_tt)
        timetable = new_tt
        message = "時間割を保存しました。"

    return render_template_string(FORM_TEMPLATE, uid=uid, timetable=timetable, weekdays=WEEKDAYS_FULL, message=message)

# FlaskのルートはAlexaリクエストハンドラへ

app.add_url_rule("/", view_func=skill_handler.verify_request_and_dispatch, methods=["POST"])

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
