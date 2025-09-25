# bot_main.py
import json
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from config import TOKEN

from shoot import register_shoot_handlers  # رجیستر هندلرهای شلیک

DATA_FILE = "data.json"
TRIGGER_KEYWORDS = ["بات هیتلر کصخله", "درود بر ضحاک"]
RESPONSE_TEXT_TEMPLATE = "{reply}\nزهر اضافه شده: {amount}\nکل زهر: {total}\nجام: {jam}, مغز: {maghz}, ایکیو: {iq}"
COOLDOWN = 120  # ثانیه (2 دقیقه)
ZOHAR_AMOUNT = 2  # مقدار زهر هر پیام

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

async def trigger_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or not update.message.text:
        return

    user = update.message.from_user
    user_id = str(user.id)
    text = update.message.text
    now = time.time()

    data = load_data()
    if user_id not in data:
        data[user_id] = DEFAULT_STATS.copy()

    last = data[user_id].get("last_zahar", 0)

    # اگر cooldown تمام شده باشه
    if now - last >= COOLDOWN:
        for trig in TRIGGER_KEYWORDS:
            if trig in text:
                data[user_id]["زهر"] = data[user_id].get("زهر", 0) + ZOHAR_AMOUNT
                data[user_id]["last_zahar"] = now

                reply_text = RESPONSE_TEXT_TEMPLATE.format(
                    reply="ممنون از شعارت بخاطر این شعارت مغزتو نمیخورم!",
                    amount=ZOHAR_AMOUNT,
                    total=data[user_id]["زهر"],
                    jam=data[user_id]["جام"],
                    maghz=data[user_id]["مغز"],
                    iq=data[user_id]["ایکیو"]
                )

                save_data(data)
                await update.message.reply_text(reply_text)
                break  # فقط اولین تریگر‌ پردازش میشه
    else:
        # در cooldown هست؛ هیچ جوابی ارسال نمیشه (مطابق خواست شما)
        pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # هندلر تریگرهای زهر
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), trigger_handler))

    # هندلرها/منطق مربوط به شلیک (مغز گرفتن)
    register_shoot_handlers(app)

    print("بات فعال شد...")
    app.run_polling()
