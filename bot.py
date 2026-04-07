import time
import requests

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "-5183949382"
STAKE_TOKEN = "4949e23dfc3974ae6de51fa29f6e4d1304aadd9cc15cc7f8dc4e485cd2cdbbd1ddf9cfcb8affea722d6a89d47c098e7f"
PROXY_USER = "oxlrjqkx"
PROXY_PASS = "5sujwxt5sfyv"
PROXY_HOST = "31.59.20.176"
PROXY_PORT = "6754"

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
query {
  sportsHighRollerBetList(limit: 10) {
    id
    amount
    currency
    odds
    iid
    fixture {
      name
      slug
    }
    user {
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
        bets = data.get("data", {}).get("sportsHighRollerBetList", [])

        for bet in bets:
            bet_id = bet.get("id", "")
            if bet_id in vistos:
                continue
            vistos.add(bet_id)

            monto = float(bet.get("amount", 0))
            odds = bet.get("odds", "")
            evento = bet.get("fixture", {}).get("name", "Desconocido")
            usuario = bet.get("user", {}).get("name", "Oculto")

            categoria, emoji = clasificar_monto(monto)
            if categoria is None:
                continue

            msg = (
                emoji + " " + categoria + " BET DETECTED\n\n"
                + "Evento: " + evento + "\n"
                + "Usuario: " + usuario + "\n"
                + "Monto: $" + str(round(monto, 2)) + "\n"
                + "Cuota: " + str(odds)
            )
            enviar_mensaje(msg)
            print("Enviado:", categoria, evento, monto)

        time.sleep(15)

    except Exception as e:
        print("ERROR GENERAL:", e)
        time.sleep(10)
