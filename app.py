from flask import Flask, render_template, request, jsonify
from google import genai
import os
import json

app = Flask(__name__)

GEMINI_API_KEY = "AQ.Ab8RN6JlNUD46yYTUtHGs1KEAhQcETmNEOby59fcWKQxsbXbRw"
client = genai.Client(api_key=GEMINI_API_KEY)

BOTS_FILE = "bots_data.json"

def load_bots():
    if os.path.exists(BOTS_FILE):
        with open(BOTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_bots(bots):
    with open(BOTS_FILE, "w", encoding="utf-8") as f:
        json.dump(bots, f, ensure_ascii=False, indent=4)

@app.route("/")
def index():
    bots = load_bots()
    return render_template("index.html", bots=bots)

@app.route("/api/save_bot", methods=["POST"])
def save_bot():
    data = request.json
    bot_name = data.get("name")
    script = data.get("script", "")
    token = data.get("token", "")

    bots = load_bots()
    bots[bot_name] = {
        "token": token,
        "script": script,
        "status": "مغلق"
    }
    save_bots(bots)
    return jsonify({"status": "success", "message": f"تم حفظ البوت {bot_name} بنجاح!"})

@app.route("/api/ai_fix", methods=["POST"])
def ai_fix():
    data = request.json
    user_prompt = data.get("prompt", "")
    current_script = data.get("script", "")
    error_log = data.get("error_log", "")

    prompt = f"""
    أنت مساعد برمجي متخصص في بوتات Discord و Python.
    الكود الحالي للبوت:
    ```python
    {current_script}
    ```
    
    سجل الأخطاء:
    {error_log}
    
    طلب المستخدم:
    {user_prompt}
    
    قم بإصلاح الكود، وأعد لي فقط الكود المعدل كاملاً.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return jsonify({"status": "success", "ai_response": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)