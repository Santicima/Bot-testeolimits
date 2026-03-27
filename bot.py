import requests

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "1572595670"

def enviar_mensaje(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

url = "https://stake.com/sports"
res = requests.get(url)

print("Chequeando deportes...")

texto = res.text.lower()

if "football" in texto or "soccer" in texto or "tennis" in texto:
    enviar_mensaje("✅ HAY EVENTOS DEPORTIVOS (bot funcionando)")
    print("FUNCIONA")
else:
    enviar_mensaje("❌ No detectó deportes")
    print("NO HAY")
