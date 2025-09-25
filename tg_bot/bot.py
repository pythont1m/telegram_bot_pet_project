from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
API_URL = os.environ.get("DJANGO_API_URL", "http://web:8000/api/flights/")  # adjust if needed

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I can search flights for you. Use /search <from> <to> <date>"
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 3:
        await update.message.reply_text("Usage: /search <from_city> <to_city> <date>")
        return

    from_city, to_city, date = args

    try:
        resp = requests.get(API_URL, params={
            "from": from_city,
            "to": to_city,
            "date": date
        })
        if resp.status_code != 200:
            await update.message.reply_text(f"Error fetching flights: {resp.json().get('error')}")
            return

        flights = resp.json()
        if not flights:
            await update.message.reply_text("No flights found 😢")
            return

        flight_data = []
        for f in flights:
            try:
                dep = f['itineraries'][0]['segments'][0]['departure']['iataCode']
                arr = f['itineraries'][0]['segments'][0]['arrival']['iataCode']
                dep_time = f['itineraries'][0]['segments'][0]['departure']['at']
                price = float(f['price']['total'])
                flight_data.append({
                    "dep": dep,
                    "arr": arr,
                    "dep_time": dep_time,
                    "price": price
                })
            except (KeyError, IndexError, ValueError):
                continue

        if not flight_data:
            await update.message.reply_text("No valid flights found 😢")
            return

        flight_data.sort(key=lambda x: x['price'])
        top_flights = flight_data[:10]

        msg_lines = [f"{f['dep']} → {f['arr']} on {f['dep_time']}: ${f['price']}" for f in top_flights]
        msg_text = "\n".join(msg_lines)

        MAX_LENGTH = 4000
        chunks = []
        while len(msg_text) > MAX_LENGTH:
            split_at = msg_text.rfind("\n", 0, MAX_LENGTH)
            if split_at == -1:
                split_at = MAX_LENGTH
            chunks.append(msg_text[:split_at])
            msg_text = msg_text[split_at:]
        chunks.append(msg_text)

        for chunk in chunks:
            await update.message.reply_text(chunk)

    except Exception as e:
        await update.message.reply_text(f"Something went wrong: {e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))

print("Bot started...")
app.run_polling()
