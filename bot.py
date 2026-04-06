import requests
import time

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "-5183949382"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

ultimo_estado = {}

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
# SCRAPING REAL (SOFASCORE)
# =========================

def obtener_voley_real():
    try:
        url = "https://api.sofascore.com/api/v1/sport/volleyball/events/live"
        res = requests.get(url, headers=HEADERS)

        print("STATUS:", res.status_code)

        data = res.json()

        partidos = []

        for ev in data.get("events", []):

            home = ev.get("homeTeam", {}).get("name", "")
            away = ev.get("awayTeam", {}).get("name", "")

            home_score = ev.get("homeScore", {}).get("current", 0)
            away_score = ev.get("awayScore", {}).get("current", 0)

            categoria = (
                ev.get("tournament", {}).get("name", "") + " " +
                ev.get("category", {}).get("name", "")
            )

            print("PARTIDO:", home, "vs", away, "|", categoria)

            # 🔥 FILTRO SUAVE
            if "arg" not in categoria.lower():
                continue

            partidos.append({
                "id": ev.get("id"),
                "match": f"{home} vs {away}",
                "score": f"{home_score}-{away_score}"
            })

        return partidos

    except Exception as e:
        print("Error scraping:", e)
        return []

# =========================
# DETECTOR
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
                f"🏐 PUNTO EN VIVO\n\n"
                f"{p['match']}\n"
                f"{ultimo_estado[match_id]} → {score}"
            )

            enviar_mensaje(msg)
            ultimo_estado[match_id] = score

# =========================
# LOOP
# =========================

while True:
    try:
        print("BUSCANDO VOLEY REAL...")

        partidos = obtener_voley_real()

        if len(partidos) == 0:
            print("No se detectaron partidos")

        detectar_cambios(partidos)

    except Exception as e:
        print("Error:", e)

    time.sleep(3)
