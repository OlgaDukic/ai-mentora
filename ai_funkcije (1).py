
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


def pozovi_tutora(pitanje, predmet=None, tema=None, razred=None):
    prompt = dohvati_prompt("tutor", predmet, tema, razred)
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


def evaluiraj_odgovor(pitanje, odgovor, predmet=None, tema=None, razred=None):
    """
    Evaluira učenikov odgovor na osnovu pitanja i dodatnog konteksta.
    Vraća standardizovani rezultat: status, ocena (1–5), feedback i opciono tip_greske.
    """
    prompt = dohvati_prompt("evaluacija", predmet, tema, razred)
    try:
        prompt_text = f"Pitanje: {pitanje}\nOdgovor učenika: {odgovor}\n{prompt}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": prompt_text}],
                temperature=0.3
            )
        except openai.error.OpenAIError as e:
            logger.warning("GPT-4o neuspešan, pokušaj fallback: %s", str(e))
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt_text}],
                temperature=0.3
            )

        output = response['choices'][0]['message']['content']
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError:
            parsed = {
                "ocena": None,
                "feedback": output.strip(),
                "tip_greske": None
            }

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

    except Exception as e:
        logger.error("Greška u evaluaciji: %s", str(e))
        return {
            "status": "error",
            "message": str(e),
            "ocena": None,
            "feedback": "Došlo je do greške u evaluaciji.",
            "tip_greske": None
        }


def generisi_preporuku(ocena, tema, tip_greske=None):
    if tip_greske == "nedostatak primera":
        return f"Pokušaj da dodaš konkretan primer iz teme '{tema}' i ponovo odgovori."
    if ocena == 1:
        return f"Odlično! Savladao si lekciju o {tema}. Možeš da pređeš na sledeći izazov!"
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
        razred="8. razred"
    )
    print(test)
    preporuka = generisi_preporuku(test["ocena"], "književnost", test.get("tip_greske"))
    print("Preporuka:", preporuka)
