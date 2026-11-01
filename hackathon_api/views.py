
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Machine
from .rag_service import generate_answer


def health_check(request):
    return JsonResponse({
        "status": "ok",
        "project": "Mrithon",
        "message": "Backend is running"
    })


@csrf_exempt
def ask_question(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed."},
            status=405
        )

    try:
        data = json.loads(request.body)

        machine_id = data.get("machine_id")
        question = data.get("question")

        if not machine_id or not question:
            return JsonResponse(
                {"error": "machine_id and question are required."},
                status=400
            )

        question = question.strip()

        if not question:
            return JsonResponse(
                {"error": "Question cannot be empty."},
                status=400
            )

        if not Machine.objects.filter(id=machine_id).exists():
            return JsonResponse(
                {"error": "Machine not found."},
                status=404
            )

        result = generate_answer(machine_id, question)

        return JsonResponse(result, status=200)

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON request."},
            status=400
        )

    except Exception as error:
        print("RAG API error:", error)
        return JsonResponse(
            {"error": "Unable to generate an answer. Check the backend logs."},
            status=500
        )
