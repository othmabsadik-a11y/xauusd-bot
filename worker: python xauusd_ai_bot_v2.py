import os
import time
import logging
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data, timeout=10)
        log.info(f"Telegram: {r.status_code}")
    except Exception as e:
        log.error(f"خطأ: {e}")

def get_gold_price():
    try:
        r = requests.get("https://api.metals.live/v1/spot/gold", timeout=5)
        data = r.json()
        return round(float(data[0].get("price", 0)), 2)
    except:
        try:
            r = requests.get("https://api.coinbase.com/v2/prices/XAU-USD/spot", timeout=5)
            return round(float(r.json()["data"]["amount"]), 2)
        except:
            return None

def get_session(hour):
    if 7 <= hour < 10:
        return "🇬🇧 London Killzone"
    elif 12 <= hour < 15:
        return "🇺🇸 New York Killzone"
    elif 0 <= hour < 3:
        return "🌏 Asia Killzone"
    return None

def main():
    log.info("بوت XAUUSD AI يبدأ...")
    send_message("🤖 <b>بوت XAUUSD AI شغّال!</b>\n\nسيرسل تحليلاً عند كل Killzone:\n🇬🇧 London: 07:00 UTC\n🇺🇸 New York: 12:00 UTC\n🌏 Asia: 00:00 UTC")

    sent_sessions = set()

    while True:
        now = datetime.now(timezone.utc)
        hour = now.hour
        minute = now.minute
        session = get_session(hour)
        session_key = str(hour)

        if session and minute == 0 and session_key not in sent_sessions:
            sent_sessions.add(session_key)
            price = get_gold_price()
            if price:
                send_message(f"🔔 <b>{session}</b>\n💰 XAUUSD: <b>{price}</b>")

        if hour == 0 and minute == 5:
            sent_sessions.clear()

        time.sleep(60)

if __name__ == "__main__":
    main()
