Uputstvo za integraciju AI funkcionalnosti – Mentora
1. Funkcionalnosti koje se implementiraju

Ovaj modul implementira AI podršku za učenike pomoću OpenAI GPT-4o modela.
Trenutno uključene funkcije su:
- `pozovi_tutora`: AI tutor koji vodi učenika kroz zadatak
- `evaluiraj_odgovor`: AI evaluator koji ocenjuje učenikov odgovor
- `generisi_preporuku`: funkcija koja daje sledeći korak učeniku
- `formiraj_roditeljski_izvestaj`: GPT generisani izveštaj roditelju na osnovu aktivnosti
- `posalji_izvestaj_roditelju`: funkcija za slanje izveštaja mejlom
- `dohvati_prompt`: bira odgovarajući prompt na osnovu konteksta (uloga, predmet, tema, razred)

2. Lokacija fajlova

- `ai_funkcije.py` – osnovne AI funkcije
- `prompt_manager.py` – logika za izbor prompta
- `mentora_prompts.json` – svi promptovi koji se pozivaju iz funkcija
- `roditeljski_izvestaj.py` – generisanje izveštaja za roditelje
- `email_servis.py` – slanje mejlom generisanog izveštaja
- `.env` – čuva OPENAI API ključ i email kredencijale

3. Šta treba integrisati u Django

- U `settings.py`: dodati podršku za učitavanje `.env` i API ključeva
- Fajl `mentora_prompts.json` smeštati u dostupnu putanju (ili bazu)
- Pozivi funkcija se rade u view-ovima gde korisnik koristi tutora, šalje odgovor, itd.
- Funkcije vraćaju string koji se koristi za prikaz, čuvanje ili dalje slanje

4. Obavezne tabele u bazi

- `Korisnik`
- `Lekcija`
- `Pitanje`
- `OdgovorUcenika`
- `Evaluacija`
- `Preporuka`
- `AIChat`
- `Prompt`
- (opciono) `Napredak`, `RoditeljskiIzvestaj`
# ai-mentora
