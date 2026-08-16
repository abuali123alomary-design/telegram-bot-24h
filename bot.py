import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 7786194199
DB_NAME = "predictions.db"
user_states = {}

def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    con = get_db()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, points INTEGER DEFAULT 0)")
    cur.execute("CREATE TABLE IF NOT EXISTS matches (id INTEGER PRIMARY KEY AUTOINCREMENT, team1 TEXT, team2 TEXT, match_time TEXT, result TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS predictions (user_id INTEGER, match_id INTEGER, prediction TEXT, PRIMARY KEY (user_id, match_id))")
    con.commit()
    con.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    con = get_db()
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?,?)", (user.id, user.first_name))
    con.commit()
    con.close()
    keyboard = [
        [InlineKeyboardButton("⚽ المباريات", callback_data="matches")],
        [InlineKeyboardButton("📝 توقعاتي", callback_data="my_predictions")],
        [InlineKeyboardButton("📢 النتائج", callback_data="reveals")],
        [InlineKeyboardButton("🏆 الصدارة", callback_data="ranking")],
        [InlineKeyboardButton("👑 توقعات الكل", callback_data="all_predictions")]
    ]
    if user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("➕ اضافة مباراة", callback_data="admin_add_match")])
        keyboard.append([InlineKeyboardButton("📊 اضافة نتيجة", callback_data="admin_add_result")])
        keyboard.append([InlineKeyboardButton("📣 تنبيه الكل", callback_data="admin_notify")])

    if update.callback_query:
        await update.callback_query.edit_message_text("🔥 بوت التوقعات", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("🔥 بوت التوقعات", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "matches":
        await query.edit_message_text("لا توجد مباريات حاليا")
    elif data == "my_predictions":
        await query.edit_message_text("لم تتوقع اي مباراة بعد")
    elif data == "reveals":
        await query.edit_message_text("لا توجد نتائج جديدة")
    elif data == "ranking":
        await query.edit_message_text("قائمة الصدارة فاضية")
    elif data == "all_predictions":
        await query.edit_message_text("لا توجد توقعات")
    elif data == "admin_add_match":
        user_states[query.from_user.id] = "waiting_match"
        await query.edit_message_text("ارسل المباراة بهذا الشكل: فريق1 - فريق2 - التاريخ والوقت")
    elif data == "admin_add_result":
        await query.edit_message_text("ارسل رقم المباراة والنتيجة")
    elif data == "admin_notify":
        await query.edit_message_text("تم ارسال التنبيه")
    else:
        await start(update, context)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id in user_states and user_states[user_id] == "waiting_match":
        if user_id == ADMIN_ID:
            await update.message.reply_text("تم اضافة المباراة: " + text)
            user_states[user_id] = None
        else:
            await update.message.reply_text("انت لست الادمن")

def main():
    print("البوت بدأ التشغيل ✅")
    init_db()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
