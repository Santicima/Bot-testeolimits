import requests

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "1572595670"

def enviar_mensaje(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    r = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })
    print("RESPUESTA TELEGRAM:")
    print(r.text)

print("INICIANDO BOT...")

enviar_mensaje("🔥 TEST BOT 🔥")

print("BOT TERMINADO")
