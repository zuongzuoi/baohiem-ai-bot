import os
import requests
from fastapi import FastAPI, Request
from openai import OpenAI

# ====== ENV ======
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

# ====== HEALTH CHECK (Render cần) ======
@app.get("/")
def root():
    return {"status": "ok"}

# ====== TELEGRAM WEBHOOK ======
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    print("UPDATE:", data)

    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if not text:
        return {"ok": True}

    # ====== GỌI OPENAI ======
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là trợ lý AI về bảo hiểm Affina. "
                        "Trả lời rõ ràng, dễ hiểu, giọng chuyên nghiệp, thân thiện."
                    )
                },
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )

        reply_text = completion.choices[0].message.content

    except Exception as e:
        reply_text = f"Lỗi AI: {str(e)}"

    # ====== TRẢ LỜI TELEGRAM ======
    send_message(chat_id, reply_text)

    return {"ok": True}


def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)
