import os
import requests
from fastapi import FastAPI, Request
from openai import OpenAI

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_DOC_TEXT = os.getenv("GOOGLE_DOC_TEXT")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    user_text = data["message"].get("text", "")

    prompt = f"""
Bạn là trợ lý tư vấn bảo hiểm phi nhân thọ.
Dưới đây là tài liệu nghiệp vụ chính thức, hãy trả lời đúng nội dung, rõ ràng, có link nếu có.

TÀI LIỆU:
{GOOGLE_DOC_TEXT}

CÂU HỎI KHÁCH:
{user_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    answer = response.choices[0].message.content

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": answer}
    )

    return {"ok": True}
