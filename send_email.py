import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from datetime import date
import os

# === CONFIGURACIÓN ===
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
FROM_EMAIL = os.getenv("EMAIL_USER")
FROM_PASSWORD = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("EMAIL_DEST")

# === ARCHIVO A ENVIAR ===
today = date.today().strftime("%Y-%m-%d")
filename = f"sharpcard_pitching_forma_{today}.pdf"

# === CONSTRUIR CORREO ===
msg = MIMEMultipart()
msg['From'] = FROM_EMAIL
msg['To'] = TO_EMAIL
msg['Subject'] = f"📊 Sharpcard – {today}"

msg.attach(MIMEText("Adjunto el análisis diario de pitcheo sharp en PDF."))

# Adjuntar PDF
with open(filename, 'rb') as f:
    part = MIMEApplication(f.read(), _subtype='pdf')
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(part)

# === ENVIAR ===
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(FROM_EMAIL, FROM_PASSWORD)
server.send_message(msg)
server.quit()

print("✅ Correo enviado con éxito.")
