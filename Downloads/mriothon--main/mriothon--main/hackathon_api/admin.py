from django.contrib import admin
from .models import Machine, Manual, Passage


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("name", "model_number")
    search_fields = ("name", "model_number")


@admin.register(Manual)
class ManualAdmin(admin.ModelAdmin):
    list_display = ("title", "machine", "revision", "uploaded_at")
    list_filter = ("machine", "revision")
    search_fields = ("title", "machine__name")


@admin.register(Passage)
class PassageAdmin(admin.ModelAdmin):
    list_display = ("manual_name", "machine", "revision", "page_number")
    list_filter = ("machine", "revision")
    search_fields = ("manual_name", "text")