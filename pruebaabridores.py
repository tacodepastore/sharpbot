import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import statsapi
from unidecode import unidecode

# Setup de fecha y archivo
today = datetime.now().strftime("%Y-%m-%d")
url_base = f"https://baseballsavant.mlb.com/probable-pitchers/?date={today}"
output_file = f"forma_pitchers_{today}.txt"

# Configurar navegador headless
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)
driver.get(url_base)
time.sleep(5)

# Paso 1: Extraer nombres de pitchers desde Savant
pitchers = []
elements = driver.find_elements(By.CSS_SELECTOR, 'a.matchup-link')
for el in elements:
    name = el.text.strip()
    link = el.get_attribute('href')
    if name and "/player_matchup?" in link:
        pitchers.append(unidecode(name))

driver.quit()

# Paso 2: Clasificación por estado
clasificados = {
    "🔥 Gran forma": [],
    "✅ Forma sólida": [],
    "⚠️ Riesgo de regresión": [],
    "🚫 Forma débil": [],
    "❌ Menos de 3 salidas": [],
    "⚠️ Error accediendo a log": [],
    "❓ No encontrado": [],
}

def analizar_forma_pitcher(nombre):
    try:
        player_id = statsapi.lookup_player(nombre)[0]['id']
    except IndexError:
        clasificados["❓ No encontrado"].append(f"{nombre}")
        return

    try:
        game_logs = statsapi.get('person', {
            'personId': player_id,
            'hydrate': 'stats(group=[pitching],type=[gameLog],season=2025)'
        })
        pitching_logs = game_logs['people'][0]['stats'][0]['splits']
    except Exception:
        clasificados["⚠️ Error accediendo a log"].append(f"{nombre}")
        return

    if len(pitching_logs) < 3:
        clasificados["❌ Menos de 3 salidas"].append(f"{nombre}")
        return

    pitching_logs.sort(key=lambda x: x['date'], reverse=True)
    ultimos = pitching_logs[:3]
    ERs = [int(j['stat']['earnedRuns']) for j in ultimos]
    detalle = ", ".join(f"{er} ER" for er in ERs)

    if all(er == 0 for er in ERs):
        clasificados["🔥 Gran forma"].append(f"{nombre} ({detalle})")
    elif ERs[0] == 0 and (ERs[1] >= 3 or ERs[2] >= 3):
        clasificados["⚠️ Riesgo de regresión"].append(f"{nombre} ({detalle})")
    elif ERs[0] <= 2 and ERs[1] <= 2 and ERs[2] <= 3:
        clasificados["✅ Forma sólida"].append(f"{nombre} ({detalle})")
    else:
        clasificados["🚫 Forma débil"].append(f"{nombre} ({detalle})")

# Paso 3: Ejecutar análisis
for nombre in pitchers:
    analizar_forma_pitcher(nombre)

# Paso 4: Exportar resultados
with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"🎯 Análisis de forma – Pitchers del {today}\n\n")
    for categoria in [
        "🔥 Gran forma", "✅ Forma sólida", "⚠️ Riesgo de regresión",
        "🚫 Forma débil", "❌ Menos de 3 salidas",
        "⚠️ Error accediendo a log", "❓ No encontrado"
    ]:
        if clasificados[categoria]:
            f.write(f"{categoria} ({len(clasificados[categoria])}):\n")
            for p in clasificados[categoria]:
                f.write(f"• {p}\n")
            f.write("\n")

print(f"✅ Análisis completado y guardado en: {output_file}")
