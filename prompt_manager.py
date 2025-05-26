
import json

# Učitavamo sve promptove iz JSON fajla
with open("mentora_prompts.json", "r", encoding="utf-8") as f:
    PROMPTOVI = json.load(f)

def dohvati_prompt(uloga, predmet=None, tema=None, razred=None):
    # Napredna logika: pokušaj specifičan prompt
    if predmet and tema and razred:
        kljuc = f"{uloga}_{predmet}{razred}_{tema.replace(' ', '').lower()}"
        if kljuc in PROMPTOVI:
            return PROMPTOVI[kljuc]["prompt"]

    # Fallback: osnovni prompt za datu ulogu
    if uloga in PROMPTOVI:
        return PROMPTOVI[uloga]["prompt"]

    return "Greška: Prompt nije pronađen."

# Primer korišćenja
if __name__ == "__main__":
    print(dohvati_prompt("tutor"))
    print(dohvati_prompt("tutor", predmet="mat", tema="razlomci", razred=5))
