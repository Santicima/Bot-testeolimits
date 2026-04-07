import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# =========================
# CONFIG
# =========================

TOKEN = "8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g"
CHAT_ID = "-5183949382"

URL = "https://stake1017.com/?c=playstakeio"

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
# SELENIUM SETUP
# =========================

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# =========================
# ESTADO
# =========================

vistos = set()

# =========================
# HELPERS
# =========================

def parsear_monto(texto):
    try:
        texto = texto.replace("$", "").replace(",", "").strip()
        return float(texto)
    except:
        return 0


def clasificar_monto(monto):
    if monto >= 100000:
        return "HUGE", "🟣"
    elif monto >= 50000:
        return "BIG", "🔴"
    elif monto >= 10000:
        return "MEDIUM", "🟠"
    elif monto >= 3000:
        return "SMALL", "🟡"
    else:
        return None, None


def abrir_stake():
    try:
        driver.get(URL)
        time.sleep(5)

        # retry si el mirror tarda o falla
        if "stake" not in driver.current_url:
            print("Reintentando carga...")
            driver.get(URL)
            time.sleep(5)

        print("URL actual:", driver.current_url)

    except Exception as e:
        print("Error abriendo stake:", e)


# =========================
# SCRAPING
# =========================

def obtener_apuestas():
    abrir_stake()

    apuestas = []

    filas = driver.find_elements(By.CSS_SELECTOR, "div[class*='row']")

    print("Filas encontradas:", len(filas))  # DEBUG

    for fila in filas:
        try:
            texto = fila.text.strip()

            if not texto:
                continue

            columnas = texto.split("\n")

            if len(columnas) < 3:
                continue

            evento = columnas[0]
            cuota = columnas[-2]
            monto_texto = columnas[-1]

            monto = parsear_monto(monto_texto)

            apuestas.append({
                "evento": evento,
                "cuota": cuota,
                "monto": monto,
                "raw": texto
            })

        except Exception as e:
            print("Error parseando fila:", e)
            continue

    return apuestas


# =========================
# LOOP PRINCIPAL
# =========================

print("🚀 Bot iniciado...")

while True:
    try:
        apuestas = obtener_apuestas()

        for a in apuestas:
            key = a["raw"]

            if key in vistos:
                continue

            vistos.add(key)

            categoria, emoji = clasificar_monto(a["monto"])

            if categoria is None:
                continue

            msg = f"""{emoji} {categoria} BET DETECTED

🎯 Evento: {a['evento']}
💸 Monto: ${a['monto']}
📊 Cuota: {a['cuota']}
"""

            enviar_mensaje(msg)

        time.sleep(15)

    except Exception as e:
        print("ERROR GENERAL:", e)
        time.sleep(10)
