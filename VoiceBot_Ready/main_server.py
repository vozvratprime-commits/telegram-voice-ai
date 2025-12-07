import os
from flask import Flask, request, jsonify, send_file
from google import genai
import requests
from flask_cors import CORS
import json

app = Flask(__name__)
# Включаем CORS для работы с телефона (обязательно!)
CORS(app)

# --- НАСТРОЙКИ (Ваши ключи) ---
# Вставьте свои ключи:
GEMINI_API_KEY = "AIzaSyAvE2ZU68PWowOx593csQtO27-ZnCeKDoA"
TELEGRAM_BOT_TOKEN = "8512856028:AAEzmZQtARQCxGm3v2FyRAOPpJ2-v2GxmeQ"
TELEGRAM_CHAT_ID = "5173175651"
# -----------------------------

# Настройка клиента Gemini
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Ошибка: Не удалось инициализировать Gemini. Проверьте ключ: {e}")


# Функция отправки в Telegram
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)


# Маршрут для отдачи HTML-файла (интерфейса)
@app.route('/')
def index():
    # Отдаем index.html, который теперь должен быть на Render
    return send_file('index.html')


# Маршрут для приема POST-запросов от клиента index.html
@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    data = request.json
    question = data.get('question', '')

    if not question:
        return jsonify({"status": "error", "message": "Вопрос/Тема отсутствует."}), 400

    print(f"Получен запрос на поиск: {question}")

    # --- ПРОМПТ ДЛЯ КОРОТКОГО ОТВЕТА (3-5 СЛОВ) ---
    prompt = f"""
    ТВОЯ РОЛЬ: Ты — эксперт-помощник, который использует Google Search для поиска информации.

    ОЧЕНЬ ВАЖНОЕ ПРАВИЛО: Ответь **максимально кратко**, используя **ТОЛЬКО 3-5 слов**. Отвечай только по теме вопроса. Используй **только маленькие буквы**.

    ВОПРОС ДЛЯ ПОИСКА:
    {question}
    """
    # ---------------------------------------------

    try:
        # Вызов Gemini с включенным инструментом Google Search
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={"tools": [{"google_search": {}}]}
        )
        answer = response.text.strip()

        print(f"Ответ ИИ: {answer}")

        # Отправка ответа пользователю в Telegram
        send_telegram(f"🔍 {answer}")

        return jsonify({"status": "success", "answer": answer})

    except Exception as e:
        error_msg = f"Ошибка Gemini API: {e}"
        print(error_msg)
        send_telegram(f"❌ Ошибка сервера: {e}")
        return jsonify({"status": "error", "message": error_msg}), 500

# Отсутствует блок if __name__ == '__main__':, так как сервер запускается через gunicorn