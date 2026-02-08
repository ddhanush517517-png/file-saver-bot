import json
import uuid
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv ("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
DB_FILE = "files.json"


def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)


files_db = load_db()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        code = context.args[0]
        if code in files_db:
            await update.message.reply_document(files_db[code])
        else:
            await update.message.reply_text("❌ Invalid link.")
    else:
        await update.message.reply_text(
            "🔒 Private File Saver Bot\nOnly owner can upload files."
        )


async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not allowed.")
        return

    msg = update.message
    file_id = None

    if msg.document:
        file_id = msg.document.file_id
    elif msg.video:
        file_id = msg.video.file_id
    elif msg.audio:
        file_id = msg.audio.file_id
    elif msg.photo:
        file_id = msg.photo[-1].file_id

    if not file_id:
        await update.message.reply_text("Send a file.")
        return

    code = str(uuid.uuid4())[:8]
    files_db[code] = file_id
    save_db(files_db)

    link = f"https://t.me/{context.bot.username}?start={code}"
    await update.message.reply_text(
        f"✅ File saved!\n\n🔗 Download link:\n{link}"
    )


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, handle_files))

print("Bot is running...")
app.run_polling()

