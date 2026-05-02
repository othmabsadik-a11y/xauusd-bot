import os
import time
import logging
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
        return round(float(r.json()[0].get("price", 0)), 2)
    except:
        try:
            r = requests.get("https://api.coinbase.com/v2/prices/XAU-USD/spot", timeout=5)
            return round(float(r.json()["data"]["amount"]), 2)
        except:
            return None

def analyze_with_gemini(price, session, time_utc):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        prompt = f"""أنت محلل XAUUSD خبير. حلل السوق الآن:
السعر: {price}
الجلسة: {session}
الوقت: {time_utc} UTC

قدم تحليلاً موجزاً:
1. Daily Bias: Bullish/Bearish
2. Setup المتوقع
3. Entry المقترح
4. SL و TP
5. القرار: BUY/SELL/انتظر
6. نسبة الثقة /10
⚠️ القرار النهائي للمتداول دائماً."""
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, json=body, timeout=30)
        result = r.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        log.error(f"خطأ Gemini: {e}")
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
    send_message("🤖 <b>بوت XAUUSD AI شغّال!</b>\n\n🇬🇧 London: 07:00 UTC\n🇺🇸 New York: 12:00 UTC\n🌏 Asia: 00:00 UTC")
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
                send_message(f"🔔 <b>{session}</b>\n💰 XAUUSD: <b>{price}</b>\n⏳ جاري التحليل...")
                analysis = analyze_with_gemini(price, session, now.strftime("%H:%M"))
                if analysis:
                    send_message(f"📊 <b>تحليل {session}</b>\n\n{analysis}")
                else:
                    send_message("⚠️ تعذر التحليل، راجع الشارت يدوياً")
        if hour == 0 and minute == 5:
            sent_sessions.clear()
        time.sleep(60)

if __name__ == "__main__":
    main()
