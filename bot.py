import time
import requests
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
STAKE_TOKEN = os.getenv("STAKE_TOKEN")
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")

PROXIES = {
    "http": "http://" + PROXY_USER + ":" + PROXY_PASS + "@" + PROXY_HOST + ":" + PROXY_PORT,
    "https": "http://" + PROXY_USER + ":" + PROXY_PASS + "@" + PROXY_HOST + ":" + PROXY_PORT,
}

HEADERS = {
    "Content-Type": "application/json",
    "x-access-token": STAKE_TOKEN,
    "Referer": "https://stake.com/",
    "Origin": "https://stake.com"
}

QUERY = """
query HighRollerBets {
  sportsBetList(limit: 10) {
    id
    amount
    currency
    odds
    fixture {
      name
    }
  }
}
"""

def enviar_mensaje(msg):
    try:
        url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("Error Telegram:", e)

def clasificar_monto(monto):
    if monto >= 100000:
        return "HUGE", "🟣"
    elif monto >= 50000:
        return "BIG", "🔴"
    elif monto >= 10000:
        return "MEDIUM", "🟠"
    elif monto >= 3000:
        return "SMALL", "🟡"
    else:
        return None, None

vistos = set()

print("Bot iniciado...")

while True:
    try:
        response = requests.post(
            "https://stake.com/_api/graphql",
            json={"query": QUERY},
            headers=HEADERS,
            proxies=PROXIES,
            timeout=20
        )
        print("Status:", response.status_code)
        print("Respuesta:", response.text[:500])

        data = response.json()
        bets = data.get("data", {}).get("sportsBetList", [])

        for bet in bets:
            bet_id = bet.get("id", "")
            if bet_id in vistos:
                continue
            vistos.add(bet_id)

            monto = float(bet.get("amount", 0))
            odds = bet.get("odds", "")
            evento = bet.get("fixture", {}).get("name", "​​​​​​​​​​​​​​​​
