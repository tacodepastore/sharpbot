from PIL import Image, ImageDraw, ImageFont
from datetime import date
import os

# Fecha y rutas dinámicas
today = date.today()
OUTPUT_PREFIX = f"sharpcard_pitching_forma_{today}"
ANALYSIS_PATH = f"matchups_completos_con_forma_{today}.txt"

if not os.path.exists(ANALYSIS_PATH):
    print(f"⛔ Archivo no encontrado: {ANALYSIS_PATH}")
    exit(1)

# Configuración general
WIDTH, HEIGHT = 1200, 1800
BACKGROUND_COLOR = (255, 255, 255)
TEXT_COLOR = (0, 0, 0)
FONT_PATH_DEFAULT = "arial.ttf"
FONT_PATH_EMOJI = "seguiemj.ttf"
LOGO_PATH = "taco_logo.png"
MATCHUPS_PER_IMAGE = 3

# Cargar fuente con fallback
def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH_EMOJI, size)
    except:
        return ImageFont.truetype(FONT_PATH_DEFAULT, size)

font_title = load_font(28)
font_body = load_font(18)
font_small = load_font(16)

# Leer archivo de análisis
with open(ANALYSIS_PATH, "r", encoding="utf-8") as f:
    lines = [line.replace("\r", "").strip() for line in f.readlines()]

# Separar bloques por matchup
blocks = []
current_block = []
for line in lines:
    if line.startswith("⚾ MATCHUP:"):
        if current_block:
            blocks.append(current_block)
            current_block = []
    current_block.append(line)
if current_block:
    blocks.append(current_block)

print(f"🔍 Total de bloques detectados: {len(blocks)}")

# Agrupar por imagen
def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

groups = list(chunk(blocks, MATCHUPS_PER_IMAGE))
image_files = []

for idx, group in enumerate(groups):
    img = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    y = 40

    # Logo
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo.thumbnail((180, 180))
        img.paste(logo, (WIDTH - 200, 20), logo)
    except:
        pass

    # Título
    draw.text((60, y), f"📊 ANÁLISIS POR MATCHUP – Parte {idx + 1}", fill=TEXT_COLOR, font=font_title)
    y += 80

    for matchup in group:
        for line in matchup:
            if not line:
                y += 10
                continue

            if set(line) <= {"=", "-"}:
                continue

            if "📌 Diagnóstico: Edge técnico dominante" in line:
                continue

            if "🟢" in line or "🟡" in line or "🔴" in line:
                color_map = {"🟢": "green", "🟡": "yellow", "🔴": "red"}
                parts = line.split(" ")
                x_cursor = 60
                for part in parts:
                    if part in color_map:
                        draw.ellipse((x_cursor, y + 4, x_cursor + 24, y + 24), fill=color_map[part], outline="black")
                        x_cursor += 32
                    else:
                        clean = part.replace("🟢", "").replace("🟡", "").replace("🔴", "")
                        draw.text((x_cursor, y), clean + " ", font=font_body, fill=TEXT_COLOR)
                        x_cursor += draw.textlength(clean + " ", font=font_body)
                y += 40
                continue

            if "Edge técnico claro" in line:
                draw.ellipse((60, y + 6, 80, y + 26), fill="green", outline="black")
                draw.text((90, y), line, font=font_body, fill=TEXT_COLOR)
                y += 40
            elif "Perfil sólido" in line:
                draw.ellipse((60, y + 6, 80, y + 26), fill="yellow", outline="black")
                draw.text((90, y), line, font=font_body, fill=TEXT_COLOR)
                y += 40
            elif "Sin edge" in line:
                draw.ellipse((60, y + 6, 80, y + 26), fill="red", outline="black")
                draw.text((90, y), line, font=font_body, fill=TEXT_COLOR)
                y += 40
            elif line.startswith("■") or line.startswith("⚾"):
                draw.text((60, y), line, font=font_title, fill=TEXT_COLOR)
                y += 50
            else:
                draw.text((60, y), line, font=font_body, fill=TEXT_COLOR)
                y += 35

        # Separador por matchup
        y += 25
        draw.line([(60, y), (WIDTH - 60, y)], fill="gray", width=2)
        y += 30

    # ✅ Guardar imagen por grupo
    output_file = f"{OUTPUT_PREFIX}_part{idx + 1}.png"
    img.save(output_file)
    image_files.append(output_file)
    print(f"✅ Imagen generada: {output_file}")

if not blocks:
    print("⛔ No hay bloques para renderizar. Verifica el archivo de entrada.")
    exit(1)

# Exportar a PDF
images = [Image.open(img).convert("RGB") for img in image_files]
pdf_output_path = f"{OUTPUT_PREFIX}.pdf"
images[0].save(pdf_output_path, save_all=True, append_images=images[1:])
print(f"📄 PDF generado: {pdf_output_path}")

# Limpiar PNGs temporales
for img_path in image_files:
    os.remove(img_path)
print("🧹 PNGs eliminadas.")

# Confirmación
if not os.path.exists(pdf_output_path):
    print(f"⛔ No se generó el archivo PDF esperado: {pdf_output_path}")
    exit(1)
else:
    print(f"✅ Archivo PDF generado exitosamente: {pdf_output_path}")
