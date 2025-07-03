import os
import openai
import json
import logging
from prompt_manager import dohvati_prompt

# Postavljanje API ključa
openai.api_key = os.getenv("OPENAI_API_KEY")

# Postavljanje logovanja
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def evaluiraj_odgovor(
    pitanje,
    odgovor,
    predmet=None,
    tema=None,
    razred=None,
    sadrzaj_lekcije=None,
    prethodne_lekcije=None,
    dozvoljeni_izvori=None
):
    """
    Evaluira učenikov odgovor uz kontekst lekcije i dozvoljene izvore.
    Vraća standardizovani rezultat: status, ocena (1–5), feedback i tip_greske.
    """

    # Pokušaj da dohvatiš prompt
    prompt = dohvati_prompt("evaluacija", predmet, tema, razred)
    
    # Ako nema prompta, koristi opšti fallback prompt
   if not prompt:
    prompt = OPSTI_PROMPTOVI.get(predmet, OPSTI_PROMPTOVI["default"])


    # Pripremi dodatni kontekst
    kontekst = ""
    if sadrzaj_lekcije:
        kontekst += f"\nKontekst lekcije:\n{sadrzaj_lekcije}\n"
    if prethodne_lekcije:
        kontekst += f"\nPrethodne lekcije:\n{prethodne_lekcije}\n"
    if dozvoljeni_izvori:
        kontekst += f"\nDozvoljeni izvori:\n{dozvoljeni_izvori}\n"

    # Finalni tekst prompta
    prompt_text = (
        f"Pitanje:\n{pitanje}\n\n"
        f"Odgovor učenika:\n{odgovor}\n"
        f"{kontekst}\n"
        f"{prompt}\n\n"
        "Vrati JSON format:\n"
        "{\n"
        '  "ocena": broj od 1 do 5,\n'
        '  "feedback": "kratak komentar",\n'
        '  "tip_greske": "opis greške ili null"\n'
        "}"
    )

    try:
        # Prvi pokušaj sa GPT-4o
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_text}
            ],
            temperature=0.3
        )
    except openai.error.OpenAIError as e:
        logger.warning("GPT-4o neuspešan, pokušaj fallback na GPT-3.5: %s", str(e))
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_text}
            ],
            temperature=0.3
        )

    # Dobijeni odgovor modela
    output = response.choices[0].message.content

    # Pokušaj da parsiraš JSON
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        logger.warning("Neuspešno parsiranje JSON-a, vraćam plain tekst.")
        parsed = {
            "ocena": None,
            "feedback": output.strip(),
            "tip_greske": None
        }

    # Validacija ocene
    ocena = parsed.get("ocena")
    try:
        ocena = int(ocena)
        if ocena not in range(1, 6):
            raise ValueError
    except:
        ocena = None

    return {
        "status": "success",
        "ocena": ocena,
        "feedback": parsed.get("feedback"),
        "tip_greske": parsed.get("tip_greske")
    }
