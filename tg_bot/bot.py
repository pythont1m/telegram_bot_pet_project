from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
FLIGHTS_API_URL = os.environ.get("DJANGO_API_URL", "http://web:8000/api/flights/")
HISTORY_API_URL = os.environ.get("DJANGO_HISTORY_API_URL", "http://web:8000/api/search-history/")
SAVE_HISTORY_URL = os.environ.get("DJANGO_SAVE_HISTORY_URL", "http://web:8000/api/save-search/")

async def ensure_user(update: Update):
    """Ensure TelegramUser exists in DB, returns user ID for history."""
    try:
        resp = requests.post(SAVE_HISTORY_URL.replace("save-search/", ""), json={
            "telegram_id": update.effective_user.id,
            "username": update.effective_user.username or ""
        })
        # Some APIs might return existing user or create new one
        return update.effective_user.id
    except Exception as e:
        print(f"⚠️ Could not ensure user: {e}")
        return update.effective_user.id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✈️ Welcome! I can help you find flights.\n\n"
        "Usage:\n"
        "👉 /search <from_city> <to_city> <date>\n"
        "👉 /history (to see your past searches)"
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 3:
        await update.message.reply_text("Usage: /search <from_city> <to_city> <date>")
        return

    from_city, to_city, date = args
    user_id = await ensure_user(update)

    try:
        resp = requests.get(FLIGHTS_API_URL, params={
            "from": from_city.upper(),
            "to": to_city.upper(),
            "date": date
        })
        if resp.status_code != 200:
            await update.message.reply_text(f"Error fetching flights: {resp.json().get('error')}")
            return

        flights = resp.json()
        if not flights:
            await update.message.reply_text("No flights found 😢")
            return

        # Save search history
        try:
            requests.post(SAVE_HISTORY_URL, json={
                "user": user_id,
                "from_city": from_city,
                "to_city": to_city,
                "date": date
            })
        except Exception as e:
            print(f"⚠️ Failed to save history: {e}")

        # Process flight data
        flight_data = []
        for f in flights:
            try:
                dep = f['itineraries'][0]['segments'][0]['departure']['iataCode']
                arr = f['itineraries'][0]['segments'][0]['arrival']['iataCode']
                dep_time = f['itineraries'][0]['segments'][0]['departure']['at']
                price = float(f['price']['total'])
                flight_data.append({"dep": dep, "arr": arr, "dep_time": dep_time, "price": price})
            except (KeyError, IndexError, ValueError):
                continue

        if not flight_data:
            await update.message.reply_text("No valid flights found 😢")
            return

        flight_data.sort(key=lambda x: x['price'])
        top_flights = flight_data[:10]

        msg_lines = [f"{f['dep']} → {f['arr']} on {f['dep_time']}: ${f['price']}" for f in top_flights]
        await update.message.reply_text("\n".join(msg_lines))

    except Exception as e:
        await update.message.reply_text(f"Something went wrong: {e}")

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = await ensure_user(update)
    try:
        resp = requests.get(HISTORY_API_URL, params={"user_id": user_id})
        if resp.status_code != 200:
            await update.message.reply_text("⚠️ Could not fetch history")
            return

        history = resp.json()
        if not history:
            await update.message.reply_text("No past searches found 🕵️")
            return

        history_sorted = sorted(history, key=lambda h: h.get("timestamp", h.get("id", 0)), reverse=True)
        msg_lines = [f"{h['from_city']} → {h['to_city']} on {h['date']}" for h in history_sorted[:5]]

        await update.message.reply_text("📝 Your recent searches:\n" + "\n".join(msg_lines))

    except Exception as e:
        await update.message.reply_text(f"Something went wrong: {e}")

# Setup bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search))
app.add_handler(CommandHandler("history", history))

print("Bot started...")
app.run_polling()
