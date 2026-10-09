import os
import asyncio
import random
from datetime import datetime
import pytz
import requests
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# তোমার Bot Info
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8658845398:AAFC5LvFvpF2F8zYdvOjMNcD1QClJ3ZMbcQ")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7270958574")
BD_TZ = pytz.timezone('Asia/Dhaka')

# সিগন্যাল এর জন্য কিছু Reason
REASONS = [
    "Order Block Retest",
    "FVG + Liquidity Grab",
    "Support/Resistance Break",
    "EMA Crossover",
    "RSI Divergence"
]

def send_telegram_signal():
    now_bd = datetime.now(BD_TZ)
    time_str = now_bd.strftime("%I:%M %p") # বাংলাদেশ টাইম
    date_str = now_bd.strftime("%Y-%m-%d")

    direction = random.choice(["UP", "DOWN"])
    emoji = "⬆️" if direction == "UP" else "⬇️"
    reason = random.choice(REASONS)

    message = f"""📊 EUR/USD SIGNAL

⏰ {time_str}
📅 {date_str} (BD Time)
💰 Pair: EUR/USD
📈 Direction: {direction} {emoji}
⏳ Time: 5 Min

Reason: {reason}
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
        print(f"Signal Sent: {time_str} - {direction}")
    except Exception as e:
        print(f"Error: {e}")

@app.get("/")
async def home():
    now_bd = datetime.now(BD_TZ).strftime("%I:%M:%S %p")
    return {"status": "Bot is Live", "bd_time": now_bd, "pair": "EUR/USD"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(signal_loop())

async def signal_loop():
    while True:
        send_telegram_signal()
        # 5 মিনিট = 300 সেকেন্ড পর পর সিগন্যাল
        await asyncio.sleep(300)
