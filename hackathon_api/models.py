
from django.db import models


class Machine(models.Model):
    name = models.CharField(max_length=150)
    model_number = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.model_number})"


class Manual(models.Model):
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name="manuals",
    )
    title = models.CharField(max_length=200)
    revision = models.CharField(max_length=50)
    pdf_file = models.FileField(upload_to="manuals/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.revision}"
