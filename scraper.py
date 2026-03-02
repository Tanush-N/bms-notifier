import os
import requests
from playwright.sync_api import sync_playwright
import random
import time

# 1. Random Jitter to avoid bot detection
sleep_time = random.randint(1, 60)
print(f"Adding random jitter: {sleep_time}s")
time.sleep(sleep_time)

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EVENT_URL = "https://in.bookmyshow.com/sports/icc-men-s-t20-world-cup-2026-semi-final-2/ET00474271"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send Telegram: {e}")

def check_bms():
    with sync_playwright() as p:
        try:
            # 2. Add a User-Agent to look like a real browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # 3. Wait until the network is quiet (all scripts loaded)
            print(f"Navigating to: {EVENT_URL}")
            page.goto(EVENT_URL, wait_until="networkidle", timeout=60000)

            content = page.content()
            
            # Check for the trigger
            if "Coming Soon" not in content:
                # We also check if the page actually loaded (looking for 'ICC' or 'T20')
                # to avoid false alarms if the page is blank or blocked
                if "T20" in content or "World Cup" in content:
                    send_telegram(f"🚨 TICKETS MIGHT BE LIVE!\nCheck now: {EVENT_URL}")
                    print("Status: Trigger detected!")
                else:
                    print("Status: Page loaded but content seems wrong (Possible Block).")
            else:
                print("Status: Still showing 'Coming Soon'...")
                
            browser.close()
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing Telegram credentials in Secrets!")
    else:
        check_bms()
