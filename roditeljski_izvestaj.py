
import openai
from prompt_manager import dohvati_prompt

# API ključ treba da bude iz .env fajla (ovde samo kao placeholder)
openai.api_key = "OVDE_STAVI_TVOJ_KLJUC"

def formiraj_roditeljski_izvestaj(ime_ucenika, razred, aktivnosti, evaluacije, preporuke):
    '''
    Formira tekst roditeljskog izveštaja na osnovu učenikovih podataka.

    - ime_ucenika: string
    - razred: int
    - aktivnosti: list of lekcija naziva
    - evaluacije: list of tekstualnih komentara
    - preporuke: list of preporuka koje je AI dao učeniku
    '''
    prompt = dohvati_prompt("roditelj_izvestaj")

    sadrzaj = f"""Učenik: {ime_ucenika}
Razred: {razred}

Aktivnosti učenika:
{chr(10).join(f"- {a}" for a in aktivnosti)}

Komentari evaluacija:
{chr(10).join(f"- {e}" for e in evaluacije)}

Preporuke koje je AI dao:
{chr(10).join(f"- {p}" for p in preporuke)}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": sadrzaj}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Greška pri generisanju roditeljskog izveštaja: {e}"
