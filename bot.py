from playwright.sync_api import sync_playwright
import requests

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "1572595670"


def enviar_mensaje(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

print("Abriendo navegador...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto("https://stake.com/sports")
    page.wait_for_timeout(5000)  # espera que cargue JS
    
    contenido = page.content().lower()
    
    if "football" in contenido or "tennis" in contenido:
        enviar_mensaje("✅ Detectó deportes (Playwright funciona)")
        print("FUNCIONA")
    else:
        enviar_mensaje("❌ No detectó deportes (Playwright)")
        print("NO DETECTÓ")
    
    browser.close()
