# shoot.py
# منطق "مغزتو میخوام" (شلیک / گرفتن ایکیو).
# این ماژول تابع register_shoot_handlers(app) را صادر می‌کند تا در اسکریپت اصلی رجیستر شود.

import json
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

DATA_FILE = "data.json"

# هزینه و میزان انتقال (قابل تغییر)
ZOHAR_COST = 10    # هزینه برای initiator (از او کم می‌شود)
IQ_TRANSFER = 20   # مقدار ایکیویی که از target کم و به initiator اضافه می‌شود

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

def ensure_user(data, user_id):
    if user_id not in data:
        data[user_id] = DEFAULT_STATS.copy()

def do_brain_take(initiator_id: str, target_id: str):
    """
    انجام تراکنش:
    - چک موجودی initiator برای زهر
    - چک موجودی target برای ایکیو
    - در صورت معتبر بودن، تغییرات را اعمال و ذخیره می‌کند
    برمی‌گرداند: (success: bool, message: str)
    """
    data = load_data()
    ensure_user(data, initiator_id)
    ensure_user(data, target_id)

    initiator = data[initiator_id]
    target = data[target_id]

    # بررسی زهر initiator
    if initiator.get("زهر", 0) < ZOHAR_COST:
        return False, f"نشد — تو فقط {initiator.get('زهر',0)} زهر داری، برای این عمل نیاز به {ZOHAR_COST} زهر داری."

    # بررسی ایکیو target
    if target.get("ایکیو", 0) < IQ_TRANSFER:
        return False, f"نشد — مخاطب فقط {target.get('ایکیو',0)} ایکیو داره که کمتر از {IQ_TRANSFER} هست."

    # انجام تراکنش (اتمی به صورت ساده: خواندن، تغییر، ذخیره)
    initiator["زهر"] -= ZOHAR_COST
    target["ایکیو"] -= IQ_TRANSFER
    initiator["ایکیو"] = initiator.get("ایکیو", 0) + IQ_TRANSFER

    save_data(data)

    msg = (
        f"عملیات موفق! {ZOHAR_COST} زهر از تو کم شد و {IQ_TRANSFER} ایکیو از مخاطب گرفته و به تو اضافه شد.\n"
        f"حالت تو — زهر: {initiator['زهر']}, ایکیو: {initiator['ایکیو']}\n"
        f"حالت مخاطب — ایکیو: {target['ایکیو']}"
    )
    return True, msg

# -------------------------
# هندلرها
# -------------------------
async def text_shoot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر متن: وقتی کاربران دقیقاً متن 'مغزتو میخوام' می‌نویسند.
    باید پیام ریپلای به پیام هدف باشد تا target مشخص شود.
    """
    if update.message is None or not update.message.text:
        return

    text = update.message.text.strip()
    if text != "مغزتو میخوام":
        return

    # باید ریپلای باشد تا target مشخص شود
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text("برای گرفتن مغز، پیام را ریپلای به پیام فرد هدف بزن.")
        return

    initiator = update.message.from_user
    target = update.message.reply_to_message.from_user

    if initiator.id == target.id:
        await update.message.reply_text("نمیتونی از خودت مغز بگیری :)")
        return

    success, msg = do_brain_take(str(initiator.id), str(target.id))
    await update.message.reply_text(msg)

async def cmd_shoot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    کامند /takebrain — باید به صورت ریپلای روی پیام فرد هدف استفاده شود.
    مثال:
    (ریپلای به پیام فرد هدف) /takebrain
    """
    if update.message is None:
        return

    # باید ریپلای باشد تا target مشخص شود
    if not update.message.reply_to_message or not update.message.reply_to_message.from_user:
        await update.message.reply_text("برای استفاده از این دستور، آن را ریپلای به پیام فرد هدف بزن.")
        return

    initiator = update.message.from_user
    target = update.message.reply_to_message.from_user

    if initiator.id == target.id:
        await update.message.reply_text("نمیتونی از خودت مغز بگیری :)")
        return

    success, msg = do_brain_take(str(initiator.id), str(target.id))
    await update.message.reply_text(msg)

def register_shoot_handlers(app):
    # هندلر متن دقیق "مغزتو میخوام"
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_shoot_handler))
    # هندلر کامند /takebrain
    app.add_handler(CommandHandler("takebrain", cmd_shoot_handler))
