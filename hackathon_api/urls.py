
from django.urls import path
from .views import health_check, ask_question

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("ask/", ask_question, name="ask_question"),
]
