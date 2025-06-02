
import openai
from prompt_manager import dohvati_prompt

# OBAVEZNO: koristi API ključ iz .env fajla (ovde placeholder)
openai.api_key = "OVDE_STAVI_TVOJ_KLJUC"

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
        return f"Greška u radu AI tutora: {e}"


def evaluiraj_odgovor(pitanje, odgovor, predmet=None, tema=None, razred=None):
    '''
    Evaluira učenikov odgovor na osnovu pitanja i dodatnog konteksta.
    Vraća standardizovani rezultat: status, ocena (1–5), feedback.
    '''
    prompt = dohvati_prompt("evaluacija", predmet, tema, razred)
    try:
        prompt_text = f"Pitanje: {pitanje}\nOdgovor učenika: {odgovor}\n{prompt}"

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt_text}],
            temperature=0.3
        )

        output = response['choices'][0]['message']['content']

        import json
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError:
            parsed = {
                "ocena": None,
                "feedback": output.strip()
            }

        return {
            "status": "success",
            "ocena": parsed.get("ocena"),
            "feedback": parsed.get("feedback")
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "ocena": None,
            "feedback": "Došlo je do greške u evaluaciji."
        }
def generisi_preporuku(ocena, tema, tip_greske=None):
    if ocena == 1:
        return f"Odlično! Savladao si lekciju o {tema}. Možeš da pređeš na sledeći izazov!"
    elif ocena == 2:
        return f"Dobro ti ide sa temom '{tema}', ali bi bilo korisno da pogledaš još jedan primer ili probaš dodatnu vežbu."
    elif ocena == 3:
        return f"Izgleda da imaš poteškoća sa '{tema}'. Preporučujem ti da se vratiš na objašnjenje lekcije i da prođeš kroz još jedan zadatak."
    else:
        return "Tvoj odgovor nije mogao biti procenjen. Probaj ponovo ili obrati se svom nastavniku."
