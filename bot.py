import requests
import json
import os
from datetime import datetime, timezone

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "-5183949382"
API_KEY = "67acd669ed652da798ba482d69c33a95"

print("bot iniciado")
ARCHIVO = "cuotas.json"
def enviar_mensaje(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"

res = requests.get(url)
data = res.json()

cuotas_actuales = {}

ahora = datetime.now(timezone.utc)

for partido in data:
    inicio = datetime.fromisoformat(partido["commence_time"].replace("Z", "+00:00"))

    # ❌ ignorar en vivo
    if inicio < ahora:
        continue

    equipos = f"{partido['home_team']} vs {partido['away_team']}"

    cuotas = []

    # 🔥 TOMAR VARIAS CASAS
    for book in partido.get("bookmakers", []):
        try:
            price = book["markets"][0]["outcomes"][0]["price"]
            cuotas.append(price)
        except:
            continue

    if len(cuotas) < 2:
        continue

    # 📊 PROMEDIO
    promedio = round(sum(cuotas) / len(cuotas), 2)

    cuotas_actuales[equipos] = promedio

# historial
if os.path.exists(ARCHIVO):
    with open(ARCHIVO, "r") as f:
        cuotas_anteriores = json.load(f)
else:
    cuotas_anteriores = {}

# 🔥 DETECCIÓN PRO
for partido, cuota in cuotas_actuales.items():
    if partido in cuotas_anteriores:
        anterior = cuotas_anteriores[partido]

        cambio = anterior - cuota

        if cambio >= 0.25:
            enviar_mensaje(
                f"🔥 STEAM MOVE DETECTADO\n\n"
                f"{partido}\n"
                f"{anterior} → {cuota}\n"
                f"Δ {round(cambio,2)}\n"
                f"💰 Posible dinero fuerte"
            )
def enviar_heartbeat():
    ahora = datetime.utcnow()

    # guardamos último envío en memoria del mensaje
    minuto_actual = ahora.hour * 60 + ahora.minute

    # solo enviar si estamos cerca de múltiplos de 60
    if minuto_actual % 60 < 5:
        enviar_mensaje("🤖 Bot activo, esperando alertas...")
# guardar
with open(ARCHIVO, "w") as f:
    json.dump(cuotas_actuales, f)

enviar_heartbeat()
print("bot terminado")
