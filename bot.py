
import requests
import json
import os
import time
from datetime import datetime, timezone

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "-5183949382"
API_KEY = "67acd669ed652da798ba482d69c33a95"

ARCHIVO = "cuotas.json"
ULTIMO_HEARTBEAT = heartbeat.json


def enviar_mensaje(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })




def enviar_heartbeat():
    ahora = datetime.now(timezone.utc)

    ultima = None

    if os.path.exists(ARCHIVO_HEART):
        with open(ARCHIVO_HEART, "r") as f:
            data = json.load(f)
            ultima = datetime.fromisoformat(data["ultima"])

    if ultima is None:
        enviar_mensaje("🤖 Bot activo, esperando alertas...")
    else:
        diferencia = (ahora - ultima).total_seconds()

        if diferencia < 3600:
            return

        enviar_mensaje("🤖 Bot activo, esperando alertas...")

    with open(ARCHIVO_HEART, "w") as f:
        json.dump({"ultima": ahora.isoformat()}, f)


# 🔁 LOOP INFINITO (CLAVE)
while True:
    try:
        print("ENTRANDO AL LOOP")

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

        # historial
        if os.path.exists(ARCHIVO):
            with open(ARCHIVO, "r") as f:
                cuotas_anteriores = json.load(f)
        else:
            cuotas_anteriores = {}

        # 🔥 detección
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

        # guardar
        with open(ARCHIVO, "w") as f:
            json.dump(cuotas_actuales, f)

        # heartbeat
        enviar_heartbeat()

        print("bot terminado")

    except Exception as e:
        print("Error:", e)

    print("ESPERANDO 5 MINUTOS...")
    time.sleep(300) 