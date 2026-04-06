import requests
import json
import os
import time
from datetime import datetime, timezone

# =========================
# CONFIG
# =========================
TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "-5183949382"
API_KEY = "67acd669ed652da798ba482d69c33a95"


ARCHIVO = "cuotas.json"
ARCHIVO_HEART = "heartbeat.json"

# =========================
# TELEGRAM
# =========================

def enviar_mensaje(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

# =========================
# HEARTBEAT
# =========================

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

# =========================
# 🔥 DETECTOR STEAM MOVES
# =========================

def detectar_steam_moves(cuotas_actuales, cuotas_anteriores):
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

# =========================
# 🔥 DETECTOR BET365 DELAY
# =========================

def detectar_delay_vs_bet365(data):
    alerts = []

    # 🔥 VALIDAR QUE DATA SEA LISTA
    if not isinstance(data, list):
        print("Data inválida en delay:", data)
        return alerts

    for partido in data:

        # 🔥 VALIDAR CADA PARTIDO
        if not isinstance(partido, dict):
            continue

        if "home_team" not in partido or "away_team" not in partido:
            continue

        equipos = f"{partido['home_team']} vs {partido['away_team']}"

        bet365_odds = None
        otras_odds = []

        for book in partido.get("bookmakers", []):
            try:
                nombre = book["title"].lower()
                cuota = book["markets"][0]["outcomes"][0]["price"]

                if "bet365" in nombre:
                    bet365_odds = cuota
                else:
                    otras_odds.append(cuota)

            except:
                continue

        if bet365_odds and len(otras_odds) > 0:
            mejor_otra = min(otras_odds)

            if bet365_odds > mejor_otra:
                diff = round(bet365_odds - mejor_otra, 2)

                if diff >= 0.2:
                    alerts.append(
                        f"⚠️ POSIBLE DELAY BET365\n\n"
                        f"{equipos}\n"
                        f"Bet365: {bet365_odds}\n"
                        f"Otras: {mejor_otra}\n"
                        f"Δ {diff}\n"
                        f"💰 Bet365 va atras"
                    )

    return alerts

# =========================
# 🔁 LOOP PRINCIPAL
# =========================

while True:
    try:
        print("ENTRANDO AL LOOP")

        url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
        res = requests.get(url)

        # 🔥 PARSEO SEGURO
        try:
            data = res.json()
        except:
            print("Error parseando JSON")
            time.sleep(300)
            continue

        if not isinstance(data, list):
            print("Respuesta inesperada:", data)
            time.sleep(300)
            continue

        cuotas_actuales = {}
        ahora = datetime.now(timezone.utc)

        for partido in data:

            if not isinstance(partido, dict):
                continue

            if "commence_time" not in partido:
                continue

            inicio = datetime.fromisoformat(partido["commence_time"].replace("Z", "+00:00"))

            # ignorar en vivo
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

        # 🔥 steam moves
        detectar_steam_moves(cuotas_actuales, cuotas_anteriores)

        # 🔥 delay vs bet365
        alerts = detectar_delay_vs_bet365(data)
        for alerta in alerts:
            enviar_mensaje(alerta)

        # guardar
        with open(ARCHIVO, "w") as f:
            json.dump(cuotas_actuales, f)

        # heartbeat
        enviar_heartbeat()

        print("BOT OK")

    except Exception as e:
        print("Error:", e)

    print("ESPERANDO 5 MINUTOS...")
    time.sleep(300)
