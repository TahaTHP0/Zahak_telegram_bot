# shoot.py
# تو این فایل منطق "مغزتو میخوام" (شلیک برای گرفتن ایکیو) قرار داره.
# این ماژول عالی شد یک تابع register_shoot_handlers(app) صادر میکنه که باید در اسکریپت اصلی فراخوانی بشه.

import json
import time
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

DATA_FILE = "data.json"

# مقادیر هزینه/مقدار انتقال
ZOHAR_COST = 10    # هزینه برای کسی که میخواد مغز رو بگیره (ازش کم میشه)
IQ_TRANSFER = 20   # مقدار ایکیو که از طرف مقابل کم و به درخواست‌کننده اضافه میشه

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def ensure_user(data, user_id):
    # ساختار پیشفرض اگه کاربر وجود نداشت
    DEFAULT_STATS = {
        "زهر": 0,
        "جام": 0,
        "مغز": 0,
        "ایکیو": 50,
        "last_zahar": 0
    }
    if user_id not in data:
        data[user_id] = DEFAULT_STATS.copy()

async def do_brain_take(initiator_id: str, target_id: str):
    """
    منطق تغییر اعداد در data.json:
    - از initiator مقدار ZOHAR_COST کم میشه (در صورت داشتن)
    - از target مقدار IQ_TRANSFER کم میشه (اگر target دارای کافی ایکیو باشه)
    - به initiator مقدار IQ_TRANSFER اضافه میشه
    برگشت: (success: bool, message: str)
    """
    data = load_data()
    ensure_user(data, initiator_id)
    ensure_user(data, target_id)

    initiator = data[initiator_id]
    target = data[target_id]

    # بررسی موجودی
    if initiator.get("زهر", 0) < ZOHAR_COST:
        return False, f"اتفاق نیفتاد — تو تنها {initiator.get('زهر',0)} زهر داری، برای این عملیات نیاز به {ZOHAR_COST} زهر داری."

    if target.get("ایکیو", 0) < IQ_TRANSFER:
        return False, f"اتفاق نیفتاد — مخاطب {target.get('ایکیو',0)} ایکیو داره که کمتر از {IQ_TRANSFER} هست."

    # انجام تراکنش
    initiator["زهر"] -= ZOHAR_COST
    target["ایکیو"] -= IQ_TRANSFER
    initiator["ایکیو"] = initiator.get("ایکیو", 0) + IQ_TRANSFER

    save_data(data)
    return True, (
        f"عملیات موفق! {ZOHAR_COST} زهر از تو کم شد و {IQ_TRANSFER} ایکیو از "
        f"{target_id} به {initiator_id} منتقل شد.\n"
        f"حالت فعلی تو — زهر: {initiator['زهر']}, ایکیو: {initiator['ایکیو']}\n"
        f"حالت فعلی طرف مقابل — ایکیو: {target['ایکیو']}"
    )

# -------------------------
# Handlerهایی که رجیستر میشن
# -------------------------

async def text_shoot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    وقتی کسی متن دقیق 'مغزتو میخوام' رو مینویسه باید این پیام به صورت reply به کسی باشه
    تا بتونیم طرف مقابل رو شناسایی کنیم. (مطابق خواست شما)
    """
    if update.message is None or not update.message.text:
        return

    text = update.message.text.strip()
    if text != "مغزتو میخوام":
        return

    # این پیام باید reply باشه تا هدف مشخص باشه
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text("برای گرفتن مغز، باید پیام رو به پیام کسی ریپلای کنی یا از دستور استفاده کنی.")
        return

    initiator = update.message.from_user
    target = update.message.reply_to_message.from_user

    if initiator.id == target.id:
        await update.message.reply_text("نمیتونی از خودت مغز بگیری :)")
        return

    success, msg = await do_brain_take(str(initiator.id), str(target.id))
    await update.message.reply_text(msg)

async def cmd_shoot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    کامند /takebrain (یا /گرفتنمغز) — انتظار داریم این کامند به صورت reply استفاده بشه:
    /takebrain
    (در ریپلای روی پیام کسی)
    """
    if update.message is None:
        return

    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text("برای استفاده از این دستور، آن را ریپلای به پیام فرد هدف بزن.")
        return

    initiator = update.message.from_user
    target = update.message.reply_to_message.from_user

    if initiator.id == target.id:
        await update.message.reply_text("نمیتونی از خودت مغز بگیری :)")
        return

    success, msg = await do_brain_take(str(initiator.id), str(target.id))
    await update.message.reply_text(msg)

def register_shoot_handlers(app):
    """
    این تابع را در اسکریپت اصلی صدا بزن تا هندلرهای مرتبط با شلیک اضافه شوند.
    """
    # هندلر متنِ دقیق "مغزتو میخوام"
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_shoot_handler))
    # هندلر کامند /takebrain (نام دلخواه میتونی عوض کنی)
    app.add_handler(CommandHandler("takebrain", cmd_shoot_handler))
