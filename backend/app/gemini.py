"""
Integration with Gemini API for generating chat responses, including Celery background task.
"""
import requests
from .config import settings
from .celery_worker import celery_app

def call_gemini_api(message: str, chat_history=None):
    """
    Call the Gemini API with a user message and optional chat history.
    Returns the AI-generated response as a string.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {"x-goog-api-key": settings.GEMINI_API_KEY}
    data = {
        "contents": [{"role": "user", "parts": [{"text": message}]}]
    }
    if chat_history:
        data["history"] = chat_history
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    return "[Gemini API error]"

@celery_app.task
def gemini_message_task(message: str, chat_history=None):
    """
    Celery task to call the Gemini API asynchronously.
    """
    return call_gemini_api(message, chat_history) 