import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# إعداد مفتاح API من متغيرات البيئة
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/ai_fix", methods=["POST"])
def ai_fix():
    if not GEMINI_API_KEY:
        return jsonify({"status": "error", "message": "لم يتم ضبط GEMINI_API_KEY في Render!"})

    data = request.json or {}
    user_prompt = data.get("prompt", "")
    current_script = data.get("script", "")
    error_log = data.get("error_log", "")

    prompt = f"""
    أنت مساعد برمجي خبير لمطور البوتات NGM.
    الكود الحالي:
    ```python
    {current_script}
    ```
    الأخطاء:
    {error_log}
    طلب المستخدم:
    {user_prompt}

    قم بإصلاح الكود وتطويره بشكل كامل وأعد الكود البرمجي فقط.
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return jsonify({"status": "success", "ai_response": response.text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))