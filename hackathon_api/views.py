from django.http import JsonResponse


def health_check(request):
    return JsonResponse({
        "status": "ok",
        "project": "Mrithon",
        "message": "Backend is running"
    })