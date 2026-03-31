from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8501813621:AAGHYhSSZRR2qCthFsTnU6WDaa7v-bI60cY"

waiting_users = []
active_chats = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇪🇹 Welcome to Ethio Anonymous Chat!\n\nUse /search to find a partner."
    )

# /search
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id in active_chats:
        await update.message.reply_text("⚠️ You are already chatting.")
        return

    if waiting_users:
        partner = waiting_users.pop(0)

        active_chats[user_id] = partner
        active_chats[partner] = user_id

        await update.message.reply_text("✅ Connected! Start chatting.")
        await context.bot.send_message(partner, "✅ Connected! Start chatting.")

    else:
        waiting_users.append(user_id)
        await update.message.reply_text("⏳ Waiting for a partner...")

# /next
async def next_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id in active_chats:
        partner = active_chats.pop(user_id)
        active_chats.pop(partner, None)

        await context.bot.send_message(partner, "⏭ Your partner left. Searching new one...")

    await search(update, context)

# /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id in active_chats:
        partner = active_chats.pop(user_id)
        active_chats.pop(partner, None)

        await context.bot.send_message(partner, "❌ Your partner left the chat.")
        await update.message.reply_text("🛑 You stopped the chat.")

    elif user_id in waiting_users:
        waiting_users.remove(user_id)
        await update.message.reply_text("❌ You left the queue.")

    else:
        await update.message.reply_text("⚠️ You are not in any chat.")

# message forwarding
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id

    if user_id in active_chats:
        partner = active_chats[user_id]
        await context.bot.send_message(partner, update.message.text)

    else:
        await update.message.reply_text("👉 Use /search to find a partner.")

# app setup
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))
app.add_handler(CommandHandler("next", next_chat))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🔥 LAWILET BOT RUNNING 🔥")

app.run_polling(