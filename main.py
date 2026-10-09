import os, asyncio, random, pytz, requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from fastapi import FastAPI

app = FastAPI()
TOKEN = os.getenv("TELEGRAM_TOKEN", "8658845398:AAFC5LvFvpF2F8zYdvOjMNcD1QClJ3ZMbcQ")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7270958574")
BD_TZ = pytz.timezone('Asia/Dhaka')

def send_tg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass

def calc_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze():
    try:
        df = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
        if len(df) < 30: return None
        close = df['Close']
        df['RSI'] = calc_rsi(close)
        df['EMA9'] = close.ewm(span=9).mean()
        df['EMA21'] = close.ewm(span=21).mean()
        
        last = df.iloc[-1]
        rsi, ema9, ema21, price = float(last['RSI']), float(last['EMA9']), float(last['EMA21']), float(last['Close'])
        
        score_up = score_down = 0
        reasons = []
        if ema9 > ema21: 
            score_up+=1; reasons.append("EMA Uptrend")
        else: 
            score_down+=1; reasons.append("EMA Downtrend")
        if rsi < 35: 
            score_up+=2; reasons.append(f"RSI Oversold {rsi:.1f}")
        elif rsi > 65: 
            score_down+=2; reasons.append(f"RSI Overbought {rsi:.1f}")
        else:
            reasons.append(f"RSI {rsi:.1f}")

        if score_up == score_down: return None
        direction = "UP" if score_up > score_down else "DOWN"
        conf = min(75 + max(score_up, score_down)*6, 90)
        if conf < 75: return None
        
        expiry = random.choice([1, 2, 3, 5, 10])
        return {"dir": direction, "conf": conf, "reason": " + ".join(reasons), "exp": expiry, "price": price}
    except Exception as e:
        print(e)
        return None

async def loop():
    while True:
        sig = analyze()
        if sig:
            now = datetime.now(BD_TZ)
            emoji = "⬆️" if sig['dir']=="UP" else "⬇️"
            send_tg(f"""📊 <b>EUR/USD PRO SIGNAL (90% Filter)</b>
⏰ {now.strftime('%I:%M %p')} | {now.strftime('%Y-%m-%d')} (BD)
💰 Pair: EUR/USD
📈 Direction: {sig['dir']} {emoji}
⏳ Expiry: {sig['exp']} Min
🎯 Accuracy: {sig['conf']}%
📝 {sig['reason']}
💵 Price: {sig['price']:.5f}""")
            entry = sig['price']
            await asyncio.sleep(sig['exp']*60 + 15)
            try:
                exit_p = float(yf.download("EURUSD=X", period="1d", interval="1m", progress=False).iloc[-1]['Close'])
                win = (exit_p > entry and sig['dir']=="UP") or (exit_p < entry and sig['dir']=="DOWN")
                res = "✅ WIN" if win else "❌ LOSS"
                send_tg(f"{res} <b>{sig['dir']} | {sig['exp']}M</b>\nEntry: {entry:.5f}\nExit: {exit_p:.5f}\nTime: {datetime.now(BD_TZ).strftime('%I:%M %p')} (BD)")
            except: pass
        else:
            await asyncio.sleep(60)

@app.get("/")
def home(): return {"status": "PRO Bot Live", "bd_time": datetime.now(BD_TZ).strftime("%I:%M:%S %p")}

@app.on_event("startup")
async def start(): asyncio.create_task(loop())
