import json
import uuid
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ====== EDIT THESE ======
BOT_TOKEN = "8323436192:AAF22ZKNhmT5NSbENb5nWF7sMizP8VH7w64" 
OWNER_ID = 2128004530                    
DB_FILE = "files.json"
# ======================

# Load saved files
def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Save files
def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

files_db = load_db()

# ====== START COMMAND ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        code = context.args[0]
        if code in files_db:
            file_type = files_db[code]["type"]
            file_id = files_db[code]["id"]

            if file_type == "photo":
                await update.message.reply_photo(file_id)
            elif file_type == "video":
                await update.message.reply_video(file_id)
            elif file_type == "audio":
                await update.message.reply_audio(file_id)
            else:
                await update.message.reply_document(file_id)
        else:
            await update.message.reply_text("❌ Invalid link.")
    else:
        await update.message.reply_text(
            "🔒 Private File Saver Bot\nOnly owner can upload files."
        )

# ====== HANDLE FILES ======
async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not allowed.")
        return

    msg = update.message
    file_id = None
    file_type = None

    if msg.document:
        file_id = msg.document.file_id
        file_type = "document"
    elif msg.video:
        file_id = msg.video.file_id
        file_type = "video"
    elif msg.audio:
        file_id = msg.audio.file_id
        file_type = "audio"
    elif msg.photo:
        file_id = msg.photo[-1].file_id
        file_type = "photo"

    if not file_id:
        await update.message.reply_text("Send a file.")
        return

    code = str(uuid.uuid4())[:8]
    files_db[code] = {"id": file_id, "type": file_type}
    save_db(files_db)

    link = f"https://t.me/{context.bot.username}?start={code}"
    await update.message.reply_text(
        f"✅ File saved!\n\n🔗 Download link:\n{link}"
    )

# ====== RUN BOT ======
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, handle_files))

print("Bot is running...")
app.run_polling()