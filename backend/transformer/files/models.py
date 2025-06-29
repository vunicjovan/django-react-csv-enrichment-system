from django.core.validators import FileExtensionValidator
from django.db import models

from ..base.enums import UploadStatus


class UploadedFile(models.Model):
    """
    Model to represent an uploaded CSV file.

    Stores metadata about the file, including the original name,
    size, upload time, and status of processing.

    It also tracks whether the file has been enriched and allows
    for linking to a parent file for enriched versions.

    Attributes:
    ---------
        - `file`: FileField to store the uploaded CSV file.
        - `original_name`: CharField to store the original name of the file.
        - `file_size`: BigIntegerField to store the size of the file in bytes.
        - `uploaded_at`: DateTimeField to store when the file was uploaded.
        - `columns`: JSONField to store column names from the CSV file.
        - `is_enriched`: BooleanField to indicate if the file has been enriched.
        - `parent_file`: ForeignKey to link to a parent file for enriched versions.
        - `status`: CharField to indicate the processing status of the file.
    """

    objects: models.Manager

    file = models.FileField(
        upload_to="%Y/%m/%d/",
        validators=[FileExtensionValidator(allowed_extensions=["csv"])],
    )
    original_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # in bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)
    columns = models.JSONField(null=True, blank=True)  # Store column names
    is_enriched = models.BooleanField(default=False)
    parent_file = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="enriched_versions",
    )
    status = models.CharField(
        max_length=10,
        choices=UploadStatus.choices(),
        default=UploadStatus.PENDING.value,
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.original_name} ({self.uploaded_at})"


class FileContent(models.Model):
    """
    Model to represent the content of an uploaded CSV file.

    Stores the parsed content of the CSV file as JSON, along with the number of processed rows.

    It is linked to the `UploadedFile` model via a OneToOneField.
    Thus, if the file is deleted, the content will also be deleted.

    Attributes:
    ---------
        - `file`: OneToOneField to link to the `UploadedFile` model.
        - `data`: JSONField to store the parsed CSV content.
        - `row_count`: IntegerField to store the number of processed rows.
    """

    objects: models.Manager

    file = models.OneToOneField(UploadedFile, on_delete=models.CASCADE, related_name="content")
    data = models.JSONField()
    row_count = models.IntegerField()

    def __str__(self) -> str:
        return f"Content for {self.file.original_name}"
