import requests

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "535031481"

def enviar_mensaje(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

url = "https://stake.com/poker/tournaments"
res = requests.get(url)

if True:
    enviar_mensaje("🚨 Hay un High Roller en Stake!")
