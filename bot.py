import requests

API_KEY = "67acd669ed652da798ba482d69c33a95"

url = f"https://api.the-odds-api.com/v4/sports/soccer_argentina_primera_division/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"

res = requests.get(url)

print("STATUS:", res.status_code)
print("RESPUESTA:", res.text)


