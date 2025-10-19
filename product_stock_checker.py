import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# === CONFIG ===
PRODUCT_URL = "https://in.amazfit.com/collections/smartwatches/products/amazfit-active"
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
HEADERS = {"User-Agent": "Mozilla/5.0 (StockChecker)"}
LAST_STATUS_FILE = "last_status.txt"

# === DISCORD NOTIFY ===
def send_discord(message: str):
    if not DISCORD_WEBHOOK_URL:
        print("No Discord webhook URL configured.")
        return
    try:
        data = {"content": message}
        resp = requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=15)
        resp.raise_for_status()
        print("✅ Discord notification sent.")
    except Exception as e:
        print("❌ Discord notification failed:", e)

# === STOCK CHECK ===
def check_stock():
    try:
        resp = requests.get(PRODUCT_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator=" ").lower()

        unavailable = ["out of stock", "sold out", "currently unavailable", "unavailable"]
        available = ["add to cart", "buy now", "in stock"]

        found_available = any(p in text for p in available)
        found_unavailable = any(p in text for p in unavailable)
        print(f"Available phrases: {found_available}, Unavailable phrases: {found_unavailable}")

        return found_available and not found_unavailable
    except Exception as e:
        print("Request failed:", e)
        return False

# === STATUS TRACKER ===
def get_last_status():
    if os.path.exists(LAST_STATUS_FILE):
        with open(LAST_STATUS_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_status(status):
    with open(LAST_STATUS_FILE, "w", encoding="utf-8") as f:
        f.write(status)

# === MAIN ===
def main():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"\n--- Running Stock Check at {now} ---")

    in_stock = check_stock()
    current_status = "IN STOCK" if in_stock else "OUT OF STOCK"
    last_status = get_last_status()

    if current_status != last_status:
        save_status(current_status)
        if in_stock:
            msg = f"✅ **Amazfit Helio Strap is IN STOCK!**\n{PRODUCT_URL}"
        else:
            msg = f"❌ Amazfit Helio Strap went OUT OF STOCK.\nChecked at {now}"
        send_discord(msg)
    else:
        print(f"No change detected ({current_status}).")

    print(f"Current status: {current_status}")

if __name__ == "__main__":
    main()