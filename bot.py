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

# هنا حط باقي الدوال حقك: button_handler و text_handler

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
