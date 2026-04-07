import time
import requests
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

QUERY = """
{
  betList(
    limit: 10
    offset: 0
    sport: true
  ) {
    bet {
      id
      amount
      odds
      game {
        name
      }
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
            timeout=15
        )
        data = response.json()
        print("Respuesta API:", data)

        bets = data.get("data", {}).get("betList", [])

        for item in bets:
            bet = item.get("bet", {})
            bet_id = bet.get("id", "")
            if bet_id in vistos:
                continue
            vistos.add(bet_id)

            monto = float(bet.get("amount", 0))
            odds = bet.get("odds", "")
            evento = bet.get("game", {}).get("name", "Desconocido")

            categoria, emoji = clasificar_monto(monto)
            if categoria is None:
                continue

            msg = (
                emoji + " " + categoria + " BET DETECTED\n\n"
                + "Evento: " + evento + "\n"
                + "Monto: $" + str(round(monto, 2)) + "\n"
                + "Cuota: " + str(odds)
            )
            enviar_mensaje(msg)
            print("Enviado:", categoria, evento, monto)

        time.sleep(15)

    except Exception as e:
        print("ERROR GENERAL:", e)
        time.sleep(10)
