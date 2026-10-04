from django.db import models


class Document(models.Model):

    title = models.CharField(
        max_length=255
    )

    file = models.FileField(
        upload_to="documents/"
    )

    extracted_text = models.TextField(
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class EvidenceChunk(models.Model):

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="evidence_chunks"
    )

    chunk_text = models.TextField()

    chunk_number = models.IntegerField()

    # Source reference
    source_reference = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    # Page number for PDFs
    page_number = models.IntegerField(
        null=True,
        blank=True
    )

    # Section / heading reference
    section_reference = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.document.title} "
            f"- Chunk {self.chunk_number}"
        )