from datetime import date
import re

# Usar fecha actual del sistema
today = date.today().isoformat()
metricas_file = f"metricas_vs_roster_{today}.txt"
forma_file = f"forma_pitchers_{today}.txt"
output_file = f"matchups_completos_con_forma_{today}.txt"

# Leer archivos
with open(metricas_file, "r", encoding="utf-8") as f:
    raw_metricas = f.read()
with open(forma_file, "r", encoding="utf-8") as f:
    raw_forma = f.read()

# Parsear forma reciente
forma_dict = {}
for bloque in raw_forma.split("\n\n"):
    if not bloque.strip():
        continue
    lines = bloque.strip().splitlines()
    categoria = lines[0].split(" (")[0].strip()
    for linea in lines[1:]:
        match = re.match(r"• (.+)", linea.strip())
        if match:
            nombre = match.group(1).split(" (")[0].strip()
            forma_dict[nombre] = categoria

# Parsear bloques de métricas
blocks = re.findall(r"# \d+\..*?(?=\n#|\Z)", raw_metricas, re.DOTALL)

def extract(block, metric):
    m = re.search(fr"{metric}:\s*([\d.]+)", block)
    return float(m.group(1)) if m else None

def classify(block):
    name = re.search(r"# \d+\. (.+)", block).group(1).strip()
    K = extract(block, "K%")
    BB = extract(block, "BB%")
    xwOBA = extract(block, "xwOBA")

    if None in [K, BB, xwOBA]:
        return name, "Datos insuficientes", "", block, (K, BB, xwOBA)

    if K >= 26 and BB <= 7 and xwOBA <= 0.280:
        lvl = "🟢 Edge técnico claro"
    elif K >= 22 and BB <= 9 and xwOBA <= 0.300:
        lvl = "🟡 Perfil sólido"
    elif K < 20 or BB > 10 or xwOBA > 0.330:
        lvl = "🔴 Sin edge"
    else:
        lvl = "🟡 Perfil sólido"

    prop = ""
    if K >= 28 and BB <= 6 and xwOBA <= 0.270:
        prop = "Sugerencia: Over Ks"
    elif K <= 17 and BB >= 10:
        prop = "Sugerencia: Under Ks"

    return name, lvl, prop, block.strip(), (K, BB, xwOBA)

evaluaciones = [classify(b) for b in blocks]

# Generar análisis por parejas
matchup_blocks = []
resumen = []

for i in range(0, len(evaluaciones), 2):
    if i + 1 >= len(evaluaciones):
        break
    p1 = evaluaciones[i]
    p2 = evaluaciones[i + 1]

    n1, l1, prop1, _, stats1 = p1
    n2, l2, prop2, _, stats2 = p2
    f1 = forma_dict.get(n1, "❓ Forma no encontrada")
    f2 = forma_dict.get(n2, "❓ Forma no encontrada")

    k1, bb1, xwoba1 = stats1
    k2, bb2, xwoba2 = stats2

    def delta(a, b): return f"{(a - b):+.2f}" if None not in [a, b] else "–"

    diferencial = f"""📊 Diferencial técnico:
K%     ➝ {delta(k1, k2)}
BB%    ➝ {delta(bb1, bb2)}
xwOBA  ➝ {delta(xwoba1, xwoba2)}"""

    if "🟢" in l1 and "🔴" in l2:
        resumen.append(f"{n1} ({l1}) vs {n2} ({l2})")
        diagnostico = "📌 Diagnóstico: Edge técnico dominante a favor de " + n1
    elif "🟢" in l2 and "🔴" in l1:
        resumen.append(f"{n2} ({l2}) vs {n1} ({l1})")
        diagnostico = "📌 Diagnóstico: Edge técnico dominante a favor de " + n2
    else:
        diagnostico = "📌 Diagnóstico: Matchup equilibrado o sin edge claro"

    match_block = f"""⚾ MATCHUP: {n1} vs {n2}

🧠 Forma reciente:
• {n1}: {f1}
• {n2}: {f2}

📈 Evaluación técnica:
{n1}: {l1} {f"➝ {prop1}" if prop1 else ""}
{n2}: {l2} {f"➝ {prop2}" if prop2 else ""}

{diferencial}

{diagnostico}
{"="*60}
"""
    matchup_blocks.append(match_block)

# Escribir salida final
with open(output_file, "w", encoding="utf-8") as f:
    f.write("🎯 RESUMEN DE MATCHUPS CON EDGE TÉCNICO CLARO (🟢 vs 🔴)\n\n")
    f.write("\n".join(resumen if resumen else ["No se encontraron matchups con edge técnico diferencial."]))
    f.write("\n\n" + "="*60 + "\n")
    f.write("\n📊 ANÁLISIS POR MATCHUP\n")
    f.write("\n".join(matchup_blocks))

# ✅ Confirmación en consola
print(f"✅ Archivo generado: {output_file}")
print(f"✅ Matchups con edge técnico: {len(resumen)}")
