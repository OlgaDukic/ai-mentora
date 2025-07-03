from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from llm_response import generate_llm_response

@csrf_exempt
def llm_chat_view(request):
    """
    Django view za opšti AI chat koristeći generate_llm_response().
    """
    if request.method != "POST":
        return JsonResponse({"error": "Samo POST zahtevi su dozvoljeni."}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Neispravan JSON payload."}, status=400)

    user_message = data.get("message")
    if not user_message:
        return JsonResponse({"error": "Polje 'message' je obavezno."}, status=400)

    # Poziv funkcije za generisanje odgovora
    odgovor = generate_llm_response(
        system_prompt=(
            "Ti si edukativni AI tutor za osnovce. "
            "Odgovaraj jednostavno, prijateljski i primereno uzrastu."
        ),
        user_message=user_message,
        temperature=0.4
    )

    return JsonResponse({
        "odgovor": odgovor
    })
