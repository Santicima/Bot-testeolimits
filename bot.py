
import requests
import json
import os

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "1572595670"
API_KEY = "67acd669ed652da798ba482d69c33a95"

ARCHIVO = "cuotas.json"

def enviar_mensaje(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

print("Buscando cambios de cuotas reales...")

url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"

try:
    res = requests.get(url)
    data = res.json()

    cuotas_actuales = {}

    for partido in data:
        equipos = f"{partido['home_team']} vs {partido['away_team']}"

        try:
            cuota = partido['bookmakers'][0]['markets'][0]['outcomes'][0]['price']
            cuotas_actuales[equipos] = cuota
        except:
            continue

    # cargar historial
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r") as f:
            cuotas_anteriores = json.load(f)
    else:
        cuotas_anteriores = {}

    # comparar cuotas
    for partido, cuota in cuotas_actuales.items():
        if partido in cuotas_anteriores:
            anterior = cuotas_anteriores[partido]

            # detectar caída fuerte
            if anterior - cuota >= 0.3:
                enviar_mensaje(
                    f"🔥 POSIBLE APUESTA GRANDE\n\n"
                    f"{partido}\n"
                    f"Cuota bajó de {anterior} → {cuota}"
                )
                print("ALERTA:", partido)

    # guardar nuevas cuotas
    with open(ARCHIVO, "w") as f:
        json.dump(cuotas_actuales, f)

except Exception as e:
    enviar_mensaje("⚠️ Error en el bot")
    print(e)

print(data)
