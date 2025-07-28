
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

# Fecha actual para URL
today = datetime.now().strftime("%Y-%m-%d")
url_base = f"https://baseballsavant.mlb.com/probable-pitchers/?date={today}"
output_file = f"metricas_vs_roster_{today}.txt"

# Configuración de navegador
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

driver.get(url_base)
time.sleep(5)

# Paso 1: Extraer nombres y links
pitchers = []
elements = driver.find_elements(By.CSS_SELECTOR, 'a.matchup-link')
for el in elements:
    name = el.text.strip()
    link = el.get_attribute('href')
    if name and "/player_matchup?" in link:
        pitchers.append((name, link))

# Paso 2: Extraer métricas de cada URL
def extract_metrics(url):
    try:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.default-table-row")))
        time.sleep(2)
        row = driver.find_elements(By.CSS_SELECTOR, "tr.default-table-row td.tr-data.align-right span")
        if not row or len(row) < 19:
            return ["0"] * 19
        return [span.text if span.text else "0" for span in row[:19]]
    except:
        return ["0"] * 19

# Paso 3: Escribir resultados
with open(output_file, "w", encoding="utf-8") as f:
    for idx, (name, link) in enumerate(pitchers, 1):
        stats = extract_metrics(link)
        formatted = (
    f"# {idx}. {name}\n"
    f"--- MÉTRICAS DE CONTACTO Y PONCHES ---\n"
    f"PA: {stats[0]} | AB: {stats[1]} | H: {stats[2]} | 2B: {stats[3]} | 3B: {stats[4]} | HR: {stats[5]} | SO: {stats[6]} | K%: {stats[7]} | Whiff%: {stats[8]}\n"
    f"--- MÉTRICAS DE CONTROL Y CALIDAD DEL CONTACTO ---\n"
    f"BB: {stats[9]} | BB%: {stats[10]} | BA: {stats[11]} | SLG: {stats[12]} | wOBA: {stats[13]} | xBA: {stats[14]} | xSLG: {stats[15]} | xwOBA: {stats[16]} | EV: {stats[17]} | LA: {stats[18]}\n\n"
)

        f.write(formatted)

driver.quit()
print(f"✅ Métricas extraídas para {len(pitchers)} pitchers. Archivo guardado como {output_file}")
