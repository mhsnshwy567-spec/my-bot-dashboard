import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# إعداد مفتاح GEMINI API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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

    قم بتحسين وإصلاح الكود وتطويره بالكامل، وأعد الكود البرمجي المعدل فقط دون أي مقدمات أو شرح.
    """

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return jsonify({"status": "success", "ai_response": response.text})
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "Quota exceeded" in err_msg:
            return jsonify({
                "status": "error", 
                "message": "⏳ وصلت للحد المسموح بالطلبات المجانية في الدقيقة. يرجى الانتظار دقيقة واحدة ثم إرسال الطلب مجدداً!"
            })
        return jsonify({"status": "error", "message": err_msg})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))