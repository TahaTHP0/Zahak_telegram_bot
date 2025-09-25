import json
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from config import TOKEN

DATA_FILE = "data.json"
TRIGGER_KEYWORDS = ["بات هیتلر کصخله", "درود بر ضحاک"]
RESPONSE_TEXT = "ممنون از شعارت بخاطر این شعارت مغزتو نمیخورم!\n 2 زهر به تو اضافه شد"
COOLDOWN = 120  # ثانیه (2 دقیقه)

# ← متغیر جدید برای مقدار زهر هر پیام
ZOHAR_AMOUNT = 2  # میتونی این عدد رو تغییر بدی

DEFAULT_STATS = {
    "زهر": 0,
    "جام": 0,
    "مغز": 0,
    "ایکیو": 50,
    "last_zahar": 0
}

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    user_id = str(update.message.from_user.id)
    text = update.message.text
    now = time.time()

    data = load_data()

    if user_id not in data:
        data[user_id] = DEFAULT_STATS.copy()

    last_time = data[user_id].get("last_zahar", 0)

    response = None
    for trigger_text in TRIGGER_KEYWORDS:
        if trigger_text in text:
            if now - last_time >= COOLDOWN:
                # ← استفاده از متغیر ZOHAR_AMOUNT
                data[user_id]["زهر"] += ZOHAR_AMOUNT
                data[user_id]["last_zahar"] = now
                response = (
                    f"{RESPONSE_TEXT}\n"
                    f"زهر اضافه شده: {ZOHAR_AMOUNT}\n"
                    f"کل زهر: {data[user_id]['زهر']}\n"
                    f"جام: {data[user_id]['جام']}, "
                    f"مغز: {data[user_id]['مغز']}, "
                    f"ایکیو: {data[user_id]['ایکیو']}"
                )
            break

    save_data(data)

    if response:
        await update.message.reply_text(response)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("بات فعال شد...")
    app.run_polling()
