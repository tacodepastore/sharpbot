import subprocess
import datetime

# Ruta explícita al ejecutable del entorno virtual
PYTHON_ENV = r"C:\Users\F505D\Desktop\mis-bots-sharp\mlb_env\Scripts\python.exe"

# Fecha dinámica para sincronizar nombres
today = datetime.date.today().strftime("%Y-%m-%d")

# Lista de scripts a ejecutar en orden
scripts = [
    "fusion_pitchers_vs_roster_savant.py",
    "pruebaabridores.py",
    "analisis_metricas_forma.py",
    "rendercompleto.py"
]

for script in scripts:
    print(f"\n▶️ Ejecutando: {script}")
    subprocess.run([PYTHON_ENV, script], check=True)

print("\n✅ Pipeline completo.")

print("✅ Pipeline completo.")
