
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()  # Učitava API ključ i email lozinku iz .env fajla

def posalji_izvestaj_roditelju(email_primatelja, ime_ucenika, tekst_izvestaja):
    """
    Šalje roditeljski izveštaj na unetu email adresu.
    """
    try:
        email_posiljalac = os.getenv("EMAIL_POSILJALAC")
        email_lozinka = os.getenv("EMAIL_LOZINKA")

        poruka = MIMEMultipart()
        poruka["From"] = email_posiljalac
        poruka["To"] = email_primatelja
        poruka["Subject"] = f"Nedeljni izveštaj za učenika {ime_ucenika}"

        poruka.attach(MIMEText(tekst_izvestaja, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_posiljalac, email_lozinka)
            server.sendmail(email_posiljalac, email_primatelja, poruka.as_string())

        return f"Izveštaj je uspešno poslat na {email_primatelja}."

    except Exception as e:
        return f"Greška pri slanju izveštaja: {e}"
