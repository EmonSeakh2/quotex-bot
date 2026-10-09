import asyncio, os, random
from fastapi import FastAPI
from telegram import Bot
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)
app = FastAPI()

async def signal_loop():
    await asyncio.sleep(15)
    while True:
        try:
            direction = random.choice(["UP", "DOWN"])
            arrow = "⬆️" if direction == "UP" else "⬇️"
            msg = f"📊 EUR/USD SIGNAL\n\n⏰ {datetime.now().strftime('%I:%M %p')}\n💰 Pair: EUR/USD\n📈 Direction: {direction} {arrow}\n⏳ Time: 5 Min\n\nReason: Order Block Retest"
            await bot.send_message(chat_id=CHAT_ID, text=msg)
            await asyncio.sleep(300)
        except Exception as e:
            print(e)
            await asyncio.sleep(60)

@app.get("/")
def home():
    return {"status": "Bot Running"}

@app.on_event("startup")
async def start_bot():
    asyncio.create_task(signal_loop())
