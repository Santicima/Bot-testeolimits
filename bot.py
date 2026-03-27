import requests
import time

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "1572595670"

def enviar_mensaje(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

ultimo_estado = False

def checkear_evento():
    global ultimo_estado

    url = "https://stake.com/poker/tournaments"
    res = requests.get(url)

    hay_hr = "High Roller" in res.text

    if hay_hr and not ultimo_estado:
        enviar_mensaje("🚨 Hay un High Roller en Stake!")

    ultimo_estado = hay_hr

while True:
    checkear_evento()
    time.sleep(300)