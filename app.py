import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# إعداد مفتاح GEMINI API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# قائمة بالنماذج المتاحة للتجربة التلقائية
MODELS_TO_TRY = [
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-2.0-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.0-pro'
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/ai_fix", methods=["POST"])
def ai_fix():
    if not GEMINI_API_KEY:
        return jsonify({"status": "error", "message": "لم يتم العثور على GEMINI_API_KEY في Render!"})

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
    الأخطاء أو الملاحظات:
    {error_log}
    طلب المستخدم للتعديل:
    {user_prompt}

    قم بتحسين وإصلاح الكود وتطويره بالكامل، وأعد الكود البرمجي المعدل فقط دون أي مقدمات.
    """

    last_error = ""
    # المحاولة والتنقل بين الموديلات تلقائياً
    for model_name in MODELS_TO_TRY:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return jsonify({"status": "success", "ai_response": response.text, "used_model": model_name})
        except Exception as e:
            last_error = str(e)
            continue # الانتقال للموديل التالي إذا فشل الحالي

    # إذا فشلت كل الموديلات يتم إرجاع آخر خطأ
    return jsonify({"status": "error", "message": f"فشلت جميع الموديلات. آخر خطأ: {last_error}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))