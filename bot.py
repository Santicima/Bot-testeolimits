import time
import requests
import os
import shutil

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("8313535097:AAGzDtX7FoWjVEDCLuX2uilhRfLSWNFLY2g")
CHAT_ID = os.getenv("-5183949382")

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
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

# 👉 encontrar automáticamente el driver
driver_path = shutil.which("chromedriver") or shutil.which("chromium-driver")

print("Driver encontrado en:", driver_path)

driver = webdriver.Chrome(
    service=Service(driver_path),
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
        texto = texto.replace("$", "").replace(",", "")
        texto = ''.join(c for c in texto if c.isdigit() or c == '.')
        return float(texto) if texto else 0
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


# =========================
# NAVEGACIÓN
# =========================

def abrir_stake():
    try:
        driver.get(URL)
        time.sleep(7)

        print("URL actual:", driver.current_url)

        # 👉 ir a Sports
        try:
            driver.find_element(By.XPATH, "//a[contains(@href, '/sports')]").click()
            time.sleep(5)
        except:
            print("No encontró botón Sports")

        # 👉 ir a High Rollers
        try:
            driver.find_element(By.XPATH, "//*[contains(text(),'High Roller')]").click()
            time.sleep(5)
        except:
            print("No encontró High Roller")

    except Exception as e:
        print("Error abriendo stake:", e)


# =========================
# SCRAPING
# =========================

def obtener_apuestas():
    abrir_stake()

    apuestas = []

    filas = driver.find_elements(
        By.XPATH,
        "//div[contains(@class,'table')]//div[contains(@class,'row')]"
    )

    print("Filas encontradas:", len(filas))

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
