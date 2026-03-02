import os
import requests
from playwright.sync_api import sync_playwright
import random
import time

# 1. Random Jitter (Human-like delay before starting)
time.sleep(random.randint(1, 30))

# Configuration from GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# The specific T20 World Cup matches you are tracking
EVENTS = [
    {
        "name": "T20 WC FINAL 🏆", 
        "url": "https://in.bookmyshow.com/sports/icc-men-s-t20-world-cup-2026-final/ET00476187"
    },
    {
        "name": "T20 WC SEMI-FINAL 2 🏏", 
        "url": "https://in.bookmyshow.com/sports/icc-men-s-t20-world-cup-2026-semi-final-2/ET00474271"
    }
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram: {e}")

def check_bms():
    with sync_playwright() as p:
        # Launching headless browser
        browser = p.chromium.launch(headless=True)
        # Setting a real browser User-Agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        for event in EVENTS:
            page = context.new_page()
            try:
                print(f"Checking {event['name']}...")
                # Wait for network to be idle to ensure JavaScript content loads
                page.goto(event['url'], wait_until="networkidle", timeout=60000)
                
                content = page.content()

                # TEST MODE: Trigger if 'ICC' is found (which it is)
                if "ICC" in content:
                    send_telegram(f"✅ TEST SUCCESS: {event['name']} check is working!")
                
                # Logic: If 'Coming Soon' is missing but the page is definitely a WC page
                if "Coming Soon" not in content:
                    if "T20" in content or "World Cup" in content:
                        send_telegram(f"🚨 TICKETS LIVE: {event['name']}!\nGrab them now: {event['url']}")
                        print(f"NOTIFICATION SENT for {event['name']}")
                    else:
                        print(f"Possible error or block on {event['name']} page.")
                else:
                    print(f"Status: {event['name']} is still 'Coming Soon'.")
                
                # Small gap between checking different events
                time.sleep(2)
                
            except Exception as e:
                print(f"Error checking {event['name']}: {e}")
            finally:
                page.close()
                
        browser.close()

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing Secrets! Check TELEGRAM_TOKEN and TELEGRAM_CHAT_ID in GitHub.")
    else:
        check_bms()
