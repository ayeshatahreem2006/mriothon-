
import os
import re

import fitz
from google import genai
from google.genai import types

from django.core.management.base import BaseCommand, CommandError

from hackathon_api.models import Manual, Passage


def split_text(text, chunk_size=1000, overlap=150):
    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


class Command(BaseCommand):
    help = "Extract PDF manuals and generate passage embeddings"

    def handle(self, *args, **options):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise CommandError("GEMINI_API_KEY is missing from .env")

        client = genai.Client(api_key=api_key)

        manuals = Manual.objects.select_related("machine").all()

        if not manuals.exists():
            raise CommandError("No manuals found.")

        for manual in manuals:
            self.stdout.write(f"Processing: {manual.title}")

            if not manual.pdf_file:
                self.stdout.write("Skipping: PDF file missing.")
                continue

            manual_name = os.path.basename(manual.pdf_file.name)
            passages_to_save = []

            try:
                with fitz.open(manual.pdf_file.path) as pdf:
                    for page_index, page in enumerate(pdf):
                        page_text = page.get_text("text")

                        for chunk in split_text(page_text):
                            response = client.models.embed_content(
                                model="gemini-embedding-001",
                                contents=chunk,
                                config=types.EmbedContentConfig(
                                    task_type="RETRIEVAL_DOCUMENT"
                                ),
                            )

                            embedding = response.embeddings[0].values

                            passages_to_save.append(
                                Passage(
                                    machine=manual.machine,
                                    manual_name=manual_name,
                                    revision=manual.revision,
                                    page_number=page_index + 1,
                                    text=chunk,
                                    embedding=embedding,
                                )
                            )

                Passage.objects.filter(
                    machine=manual.machine,
                    manual_name=manual_name,
                    revision=manual.revision,
                ).delete()

                Passage.objects.bulk_create(passages_to_save)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Saved {len(passages_to_save)} passages from {manual_name}"
                    )
                )

            except Exception as error:
                raise CommandError(
                    f"Failed to process {manual_name}: {error}"
                )

        self.stdout.write(
            self.style.SUCCESS("Manual ingestion completed.")
        )
