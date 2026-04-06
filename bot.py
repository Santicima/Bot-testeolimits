import requests
import time
from datetime import datetime

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "-5183949382"


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
# ESTADO
# =========================

ultimo_estado = {}

# =========================
# SOFASCORE (MEJORADO + DEBUG)
# =========================

def obtener_partidos_voley():
    try:
        url = "https://api.sofascore.com/api/v1/sport/volleyball/events/today"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        data = res.json()

        partidos = []

        for ev in data.get("events", []):

            if not isinstance(ev, dict):
                continue

            # 🔥 CATEGORIA COMPLETA
            categoria = (
                ev.get("tournament", {}).get("name", "") + " " +
                ev.get("category", {}).get("name", "")
            )

            # 🔍 DEBUG (ver en logs)
            print("TORNEO:", categoria)

            # 🔥 FILTRO ARGENTINA FLEXIBLE
            if "arg" not in categoria.lower():
                continue

            home = ev.get("homeTeam", {}).get("name", "Local")
            away = ev.get("awayTeam", {}).get("name", "Visitante")

            home_score = ev.get("homeScore", {}).get("current", 0)
            away_score = ev.get("awayScore", {}).get("current", 0)

            # 🔥 DETECTAR SI YA EMPEZÓ (MEJOR QUE STATUS)
            if home_score == 0 and away_score == 0:
                continue

            partidos.append({
                "id": ev.get("id"),
                "match": f"{home} vs {away}",
                "score": f"{home_score}-{away_score}"
            })

        return partidos

    except Exception as e:
        print("Error SofaScore:", e)
        return []

# =========================
# DETECTOR DE CAMBIOS
# =========================

def detectar_cambios(partidos):
    global ultimo_estado

    for p in partidos:
        match_id = p["id"]
        score = p["score"]

        if match_id not in ultimo_estado:
            ultimo_estado[match_id] = score
            continue

        if ultimo_estado[match_id] != score:
            msg = (
                f"🏐 CAMBIO EN VIVO\n\n"
                f"{p['match']}\n"
                f"{ultimo_estado[match_id]} → {score}"
            )

            enviar_mensaje(msg)
            ultimo_estado[match_id] = score

# =========================
# LOOP PRINCIPAL
# =========================

while True:
    try:
        print("BUSCANDO PARTIDOS...")

        partidos = obtener_partidos_voley()

        if len(partidos) == 0:
            print("No hay voley argentino en vivo")

        detectar_cambios(partidos)

    except Exception as e:
        print("Error:", e)

    time.sleep(5)
