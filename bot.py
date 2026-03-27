import requests

TOKEN = "TU_TOKEN"
CHAT_ID = "TU_CHAT_ID"

def enviar_mensaje(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

url = "https://stake.com/poker/tournaments"
res = requests.get(url)

if "High Roller" in res.text:
    enviar_mensaje("🚨 Hay un High Roller en Stake!")
