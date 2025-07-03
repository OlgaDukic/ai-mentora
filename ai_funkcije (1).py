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

# Opšti promptovi po predmetima
OPSTI_PROMPTOVI = {
    "srpski jezik": (
        "Uporedi učenikov odgovor sa tačnim odgovorom i kontekstom lekcije. "
        "Ako je potrebno, koristi informacije iz dozvoljenih izvora. "
        "Odgovori samo: TAČNO, DELIMIČNO ili NETAČNO. "
        "Obrazloži jednom rečenicom."
    ),
    "matematika": (
        "Uporedi učenikov odgovor sa tačnim odgovorom i kontekstom lekcije. "
        "Nemoj koristiti dodatne izvore. "
        "Oceni samo tačnost postupka i rezultata. "
        "Odgovori samo: TAČNO, DELIMIČNO ili NETAČNO. "
        "Obrazloži jednom rečenicom."
    ),
    "default": (
        "Uporedi učenikov odgovor sa tačnim odgovorom i kontekstom lekcije. "
        "Odgovori samo: TAČNO, DELIMIČNO ili NETAČNO. "
        "Obrazloži jednom rečenicom."
    )
}

# Dozvoljeni izvori po predmetima
OPSTI_DOZVOLJENI_IZVORI = {
    "srpski jezik": "https://pravopis.rs, https://vukajlija.rs",
    "matematika": "",
    "default": ""
}


def pozovi_tutora(pitanje, predmet=None, tema=None, razred=None):
    """
    Tutor funkcija - daje objašnjenje na osnovu pitanja i konteksta.
    """
    prompt = dohvati_prompt("tutor", predmet, tema, razred)
    if not prompt:
        prompt = (
            "Tvoja uloga je da odgovaraš učeniku na jednostavan i razumljiv način, primeren uzrastu. "
            "Ako znaš odgovor, objasni ga jasno i kratko."
        )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": pitanje}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Greška u radu AI tutora: %s", str(e))
        return f"Greška u radu AI tutora: {e}"


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
    Vraća status, ocenu (1–5), feedback i tip greške.
    """
    # Dohvati prompt
    prompt = dohvati_prompt("evaluacija", predmet, tema, razred)
    if not prompt:
        prompt = OPSTI_PROMPTOVI.get(predmet, OPSTI_PROMPTOVI["default"])

    # Odredi dozvoljene izvore
    if not dozvoljeni_izvori:
        dozvoljeni_izvori = OPSTI_DOZVOLJENI_IZVORI.get(predmet, OPSTI_DOZVOLJENI_IZVORI["default"])

    # Sastavi dodatni kontekst
    kontekst = ""
    if sadrzaj_lekcije:
        kontekst += f"\nKontekst lekcije:\n{sadrzaj_lekcije}\n"
    if prethodne_lekcije:
        kontekst += f"\nPrethodne lekcije:\n{prethodne_lekcije}\n"
    if dozvoljeni_izvori:
        kontekst += f"\nDozvoljeni izvori:\n{dozvoljeni_izvori}\n"

    # Finalni prompt tekst
    prompt_text = (
        f"Pitanje:\n{pitanje}\n\n"
        f"Odgovor učenika:\n{odgovor}\n"
        f"{kontekst}\n"
        f"{prompt}\n\n"
        "Vrati JSON format:\n"
        "{\n"
        '  \"ocena\": broj od 1 do 5,\n'
        '  \"feedback\": \"kratak komentar\",\n'
        '  \"tip_greske\": \"opis greške ili null\"\n'
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
        logger.warning("GPT-4o neuspešan, fallback na GPT-3.5: %s", str(e))
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_text}
            ],
            temperature=0.3
        )

    # Odgovor modela
    output = response.choices[0].message.content

    # Parsiranje JSON
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


def generisi_preporuku(ocena, tema, tip_greske=None):
    """
    Na osnovu ocene i tipa greške generiše preporuku za učenika.
    """
    if tip_greske == "nedostatak primera":
        return f"Pokušaj da dodaš konkretan primer iz teme '{tema}' i ponovo odgovori."
    if ocena == 1:
        return f"Odlično! Savladao si lekciju o '{tema}'. Možeš da pređeš na sledeći izazov!"
    elif ocena == 2:
        return f"Dobro ti ide sa temom '{tema}', ali bi bilo korisno da pogledaš još jedan primer ili probaš dodatnu vežbu."
    elif ocena == 3:
        return f"Izgleda da imaš poteškoća sa '{tema}'. Preporučujem ti da se vratiš na objašnjenje lekcije i da prođeš kroz još jedan zadatak."
    else:
        return "Tvoj odgovor nije mogao biti procenjen. Probaj ponovo ili obrati se svom nastavniku."


# Ručno testiranje iz komandne linije
if __name__ == "__main__":
    test = evaluiraj_odgovor(
        pitanje="Ko je napisao roman Na Drini ćuprija?",
        odgovor="Ivo Andrić",
        predmet="srpski jezik",
        tema="književnost",
        razred="8. razred",
        sadrzaj_lekcije="Roman Na Drini ćuprija je delo Ive Andrića koje opisuje sudbine ljudi oko mosta u Višegradu.",
        prethodne_lekcije="Učenici su učili o književnim vrstama i poznatim piscima.",
        dozvoljeni_izvori=None
    )
    print(test)
    preporuka = generisi_preporuku(test["ocena"], "književnost", test.get("tip_greske"))
    print("Preporuka:", preporuka)
