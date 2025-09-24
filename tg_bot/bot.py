from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv
from .flight_service import search_flights

load_dotenv()
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Bot is doing shit💩")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 3:
        await update.message.reply_text("Usage: /search <from_city> <to_city> <date>")
        return

    from_city, to_city, date = args
    flights = search_flights(from_city, to_city, date)  # <-- call our service

    msg = "\n".join(
        [f"{f['from']} → {f['to']} on {f['date']}: ${f['price']}" for f in flights]
    )
    await update.message.reply_text(msg)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))

print("Bot started...")
app.run_polling()  # starts long-polling
