import time
import requests
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
STAKE_TOKEN = os.getenv("4949e23dfc3974ae6de51fa29f6e4d1304aadd9cc15cc7f8dc4e485cd2cdbbd1ddf9cfcb8affea722d6a89d47c098e7f")

HEADERS = {
    "Content-Type": "application/json",
    "x-access-token": STAKE_TOKEN
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
            "https://api.stake.com/graphql",
            json={"query": QUERY},
            headers=HEADERS,
            timeout=15
        )
        print("Status:", response.status_code)
        data = response.json()
        print("Respuesta:", str(data)[:500])

        bets = data.get("data", {}).get("sportsBetList", [])

        for bet in bets:
            bet_id = bet.get("id", "")
            if bet_id in vistos:
                continue
            vistos.add(bet_id)

            monto = float(bet.get("amount", 0))
            odds = bet.get("odds", "")
            evento = bet.get("fixture", {}).get("name", "Desconocido")

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
