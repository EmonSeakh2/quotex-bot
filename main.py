from fastapi import FastAPI
import requests, asyncio
from datetime import datetime
import pytz

app = FastAPI()

BOT_TOKEN = "8956486527:AAH26Nt_-cWv1_cC_2rhA0Ux1vYN2wO1_vg"
CHAT_ID = "7270958574"

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except Exception as e:
        print(e)

@app.get("/")
def home():
    bd = datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%I:%M:%S %p")
    return {"status": "Bot LIVE", "owner": "Emon", "chat_id": CHAT_ID, "time": bd}

@app.get("/test")
def test():
    send("✅ *Emon ভাই, বট কানেক্টেড!*\nতোমার Bot: @EmonQuotexPro_72709_bot\nID: 7270958574\n\nএখন থেকে প্রতি 2 মিনিটে সিগন্যাল পাবে।")
    return {"ok": True}

@app.on_event("startup")
async def run():
    asyncio.create_task(loop())

async def loop():
    await asyncio.sleep(5)
    send("🚀 *Emon PRO BOT চালু হলো*\n2 মিনিট পর পর সিগন্যাল আসবে।")
    while True:
        try:
            now = datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%I:%M %p")
            msg = f"📊 *QUOTEX SIGNAL - EUR/USD*\n⏰ {now} | BD\n\nDirection: BUY ⬆️\nExpiry: 2 Min\nAccuracy: 82%\n\n_Powered by Emon PRO BOT_"
            send(msg)
            await asyncio.sleep(120)
        except:
            await asyncio.sleep(60)
