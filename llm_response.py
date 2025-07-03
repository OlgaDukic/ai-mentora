import os
import openai
import logging

# Postavljanje API ključa
openai.api_key = os.getenv("OPENAI_API_KEY")

# Postavljanje logovanja
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_llm_response(system_prompt, user_message, temperature=0.3, model="gpt-4o"):
    """
    Generiše slobodan odgovor GPT modela.
    
    - system_prompt: opis uloge AI-ja (kontekst)
    - user_message: korisnikovo pitanje
    - temperature: kreativnost odgovora
    - model: naziv modela (default: gpt-4o)
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Greška u generate_llm_response: %s", str(e))
        return f"Greška u generisanju odgovora: {e}"
