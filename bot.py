import requests
import json
import os
import time
from datetime import datetime, timezone

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "-5183949382"
API_KEY = "TU_API_KEY"

ARCHIVO = "cuotas.json"

ULTIMO_HEARTBEAT = None

def enviar_mensaje(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

def enviar_heartbeat():
    global ULTIMO_HEARTBEAT

    ahora = datetime.now(timezone.utc)
    hora_actual = ahora.strftime("%Y-%m-%d %H")

    if ULTIMO_HEARTBEAT != hora_actual:
        enviar_mensaje("🤖 Bot activo, esperando alertas...")
        ULTIMO_HEARTBEAT = hora_actual

# 🔁 LOOP REAL
while True:
    try:
        print("bot iniciado")

        url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
        res = requests.get(url)
        data = res.json()

        cuotas_actuales = {}
        ahora = datetime.now(timezone.utc)

        for partido in data:
            inicio = datetime.fromisoformat(partido["commence_time"].replace("Z", "+00:00"))

            if inicio < ahora:
                continue

            equipos = f"{partido['home_team']} vs {partido['away_team']}"

            cuotas = []

            for book in partido.get("bookmakers", []):
                try:
                    price = book["markets"][0]["outcomes"][0]["price"]
                    cuotas.append(price)
                except:
                    continue

            if len(cuotas) < 2:
                continue

            promedio = round(sum(cuotas) / len(cuotas), 2)
            cuotas_actuales[equipos] = promedio

        if os.path.exists(ARCHIVO):
            with open(ARCHIVO, "r") as f:
                cuotas_anteriores = json.load(f)
        else:
            cuotas_anteriores = {}

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

        with open(ARCHIVO, "w") as f:
            json.dump(cuotas_actuales, f)

        enviar_heartbeat()

        print("bot terminado")

    except Exception as e:
        print("Error:", e)

    time.sleep(300)