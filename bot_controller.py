import re
import logging
from funkcije_ai import evaluiraj_odgovor, pozovi_tutora, generisi_preporuku

logger = logging.getLogger(__name__)

def detect_intent(message):
    """
    Jednostavna detekcija namere iz korisničke poruke.
    Vraća: 'evaluacija', 'tutor', ili 'opste'
    """
    # Ako poruka sadrži ključne reči za proveru odgovora
    evaluacija_keywords = ["proveri", "da li je tačno", "oceni", "je li tačno"]
    for kw in evaluacija_keywords:
        if kw in message.lower():
            return "evaluacija"

    # Ako poruka sadrži molbu za pomoć
    tutor_keywords = ["ne znam", "objasni", "pomozi", "kako", "možeš li"]
    for kw in tutor_keywords:
        if kw in message.lower():
            return "tutor"

    # Ako ništa ne prepozna
    return "opste"


def process_user_message(message, context=None):
    """
    Glavna funkcija za procesiranje poruke učenika.
    context = dict sa ključevima:
        - predmet
        - tema
        - razred
        - sadrzaj_lekcije
        - prethodne_lekcije
        - dozvoljeni_izvori
    """

    if context is None:
        context = {}

    intent = detect_intent(message)
    logger.info(f"Prepoznata namera: {intent}")

    # Ako je učenik tražio proveru odgovora
    if intent == "evaluacija":
        rezultat = evaluiraj_odgovor(
            pitanje="",
            odgovor=message,
            predmet=context.get("predmet"),
            tema=context.get("tema"),
            razred=context.get("razred"),
            sadrzaj_lekcije=context.get("sadrzaj_lekcije"),
            prethodne_lekcije=context.get("prethodne_lekcije"),
            dozvoljeni_izvori=context.get("dozvoljeni_izvori")
        )
        preporuka = generisi_preporuku(
            ocena=rezultat.get("ocena"),
            tema=context.get("tema"),
            tip_greske=rezultat.get("tip_greske")
        )
        return {
            "tip": "evaluacija",
            "rezultat": rezultat,
            "preporuka": preporuka
        }

    # Ako je učenik tražio pomoć
    elif intent == "tutor":
        tutor_odgovor = pozovi_tutora(
            pitanje=message,
            predmet=context.get("predmet"),
            tema=context.get("tema"),
            razred=context.get("razred")
        )
        return {
            "tip": "tutor",
            "odgovor": tutor_odgovor
        }

    # Ako je opšte pitanje (fallback tutor)
    else:
        tutor_odgovor = pozovi_tutora(
            pitanje=message
        )
        return {
            "tip": "opste",
            "odgovor": tutor_odgovor
        }
