
from PIL import Image
import pytesseract
import speech_recognition as sr
from django.http import JsonResponse
from ai_funkcije import evaluiraj_odgovor

# ================================
# Ekstrakcija teksta iz slike (OCR)
# ================================
def ekstraktuj_tekst_iz_slike(image_file):
    '''
    Prima sliku (npr. rukom pisan odgovor), vraća prepoznat tekst.
    '''
    try:
        image = Image.open(image_file)
        tekst = pytesseract.image_to_string(image, lang='srp')  # koristi 'eng' za engleski jezik
        return tekst.strip()
    except Exception as e:
        return f"[Greška u OCR]: {e}"

# ================================
# Konverzija govora u tekst (Speech-to-Text)
# ================================
def audio_u_tekst(audio_file):
    '''
    Prima .wav audio fajl (npr. učenik odgovara glasom), vraća prepoznat tekst.
    '''
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)
        tekst = r.recognize_google(audio, language='sr-RS')  # koristi 'en-US' za engleski
        return tekst.strip()
    except Exception as e:
        return f"[Greška u prepoznavanju govora]: {e}"

# ================================
# Django VIEW funkcija za evaluaciju
# ================================
def evaluacija_view(request):
    '''
    Django view koji prima POST zahtev sa jednim od sledećih inputa:
    - tekstualni odgovor
    - slika sa tekstom
    - audio sa govorom

    Na osnovu toga izvlači tekst, poziva evaluaciju i vraća rezultat kao JSON.
    '''
    if request.method == 'POST':
        tip = request.POST.get('tip_odgovora')
        pitanje = request.POST.get('pitanje', '')

        if tip == 'tekst':
            tekst = request.POST.get('odgovor_tekst', '')
        elif tip == 'slika':
            slika = request.FILES.get('odgovor_slika')
            tekst = ekstraktuj_tekst_iz_slike(slika)
        elif tip == 'audio':
            audio = request.FILES.get('odgovor_audio')
            tekst = audio_u_tekst(audio)
        else:
            return JsonResponse({ "status": "error", "message": "Nepoznat tip odgovora." })

        rezultat = evaluiraj_odgovor(pitanje, tekst)
        return JsonResponse(rezultat)

    return JsonResponse({ "status": "error", "message": "Dozvoljeni su samo POST zahtevi." })
