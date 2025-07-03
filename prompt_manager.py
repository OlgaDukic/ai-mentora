import json

# Učitavamo sve promptove iz JSON fajla
with open("mentora_prompts.json", "r", encoding="utf-8") as f:
    PROMPTOVI = json.load(f)

def dohvati_prompt(uloga, predmet=None, tema=None, razred=None):
    """
    Dohvata prompt za datu ulogu, predmet, temu i razred.
    Prioritet:
    1. Specifičan prompt za predmet+razred+temu
    2. Opšti prompt za ulogu
    3. None
    """
    if predmet and tema and razred:
        kljuc = f"{uloga}_{predmet}{razred}_{tema.replace(' ', '').lower()}"
        if kljuc in PROMPTOVI:
            return PROMPTOVI[kljuc]["prompt"]
    if uloga in PROMPTOVI:
        return PROMPTOVI[uloga]["prompt"]
    return None

# Primer korišćenja
if __name__ == "__main__":
    print(dohvati_prompt("evaluacija"))
    print(dohvati_prompt("evaluacija", predmet="srpskijezik", tema="padezi", razred=5))
    print(dohvati_prompt("evaluacija", predmet="matematika", tema="razlomci", razred=6))
    print(dohvati_prompt("evaluacija", predmet="matematika", tema="deljivost", razred=6))
