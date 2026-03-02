import os
import requests
from playwright.sync_api import sync_playwright

# Configuration from Environment Variables (Set these in GitHub Secrets)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EVENT_URL = "https://in.bookmyshow.com/sports/icc-men-s-t20-world-cup-2026-semi-final-2/ET00474271"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

def check_bms():
    with sync_playwright() as p:
        # Launch browser in headless mode (perfect for GitHub Actions)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(EVENT_URL)
        
        # We wait for the "Book" button or look for the "Coming Soon" text
        content = page.content()
        
        if "Book" in content and "Coming Soon" not in content:
            send_telegram(f"🚨 TICKETS LIVE! Go to: {EVENT_URL}")
            print("Status: Tickets Available!")
        else:
            print("Status: Still waiting...")
            
        browser.close()

if __name__ == "__main__":
    check_bms()
