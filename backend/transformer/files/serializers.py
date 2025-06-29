from typing import Any

from rest_framework import serializers

from .models import UploadedFile
from ..base.constants import FileSizeConstants
from ..base.enums import SizeUnit


class UploadedFileSerializer(serializers.ModelSerializer):
    """
    Serializer for `UploadedFile` model.
    Handles the representation of uploaded files, including file metadata.
    It also formats the file size into a human-readable format.
    """

    file_size_formatted = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFile

        fields = [
            "id",
            "file",
            "original_name",
            "file_size",
            "file_size_formatted",
            "uploaded_at",
            "columns",
            "is_enriched",
            "parent_file",
            "status",
        ]

        read_only_fields = [
            "original_name",
            "file_size",
            "columns",
            "is_enriched",
            "parent_file",
            "status",
        ]

    def get_file_size_formatted(self, obj: UploadedFile) -> str:
        """
        Converts the file size into a human-readable format using the `SizeUnit` enum by
        iterating through the `SizeUnit` enum values and formating the file size accordingly.

        Returns a string representation of the file size with one decimal place and the appropriate unit.

        Used to provide a more user-friendly display of file sizes in the API response.

        Parameters
        ----------
        obj : UploadedFile
            The `UploadedFile` instance for which the file size needs to be formatted.

        Returns
        -------
        str
            A string representing the file size in a human-readable format, e.g., "1.5 MB", "500 KB", etc.
        """

        for unit in SizeUnit.values():
            if obj.file_size < 1024:
                return f"{obj.file_size:.1f} {unit}"
            obj.file_size /= 1024

        return f"{obj.file_size:.1f} GB"


class FileUploadInputSerializer(serializers.Serializer):
    """
    Serializer for file upload input.
    Validates the uploaded file to ensure it is a CSV file, checks its size,
    and ensures that a file with the same name does not already exist in the database.

    Attributes
    ----------
    file : serializers.FileField
        The file to be uploaded. It must be a CSV file and meet size requirements.

    Raises
    ------
    serializers.ValidationError
        If the file is not a CSV, if its size is below the minimum limit, exceeds the maximum limit,
        or if a file with the same name already exists in the database.
    """

    file = serializers.FileField()

    def validate_file(self, value: Any) -> Any:
        """
        Validates the uploaded file to ensure it meets the requirements:
            - The file must be a CSV file (i.e., its name must end with ".csv").
            - The file size must be greater than 0 bytes and less than or equal to 100 MB.
            - A file with the same name must not already exist in the database.

        Parameters
        ----------
        value : Any
            The uploaded file to be validated.

        Returns
        -------
        Any
            The validated file if it meets all the criteria.
        """

        if not value.name.endswith(".csv"):
            raise serializers.ValidationError("Only CSV files are allowed.")

        if value.size <= FileSizeConstants.MIN_FILE_SIZE:
            raise serializers.ValidationError("File size is below the minimum limit of 0 bytes.")

        if value.size > FileSizeConstants.MAX_FILE_SIZE:
            raise serializers.ValidationError("File size exceeds the maximum limit of 100 MB.")

        if UploadedFile.objects.filter(original_name=value.name).exists():
            raise serializers.ValidationError("A file with this name already exists.")

        return value


class FilePreviewInputSerializer(serializers.Serializer):
    """
    Serializer for file preview input.
    Validates pagination parameters for previewing file content.

    Attributes
    ----------
    page : serializers.IntegerField
        The page number to retrieve, must be greater than or equal to 1.
    page_size : serializers.IntegerField
        The number of rows per page, must be greater than or equal to 1.
    """

    page = serializers.IntegerField(min_value=1, default=1)
    page_size = serializers.IntegerField(min_value=1, default=100)


class FilePreviewOutputSerializer(serializers.Serializer):
    """
    Serializer for file preview output.
    Represents a paginated view of the file content, including column names,
    rows of data, and pagination metadata.

    Attributes
    ----------
    columns : serializers.ListField
        A list of column names in the file.
    rows : serializers.ListField
        A list of rows, where each row is represented as a dictionary.
    row_count : serializers.IntegerField
        The total number of rows in the file.
    current_page : serializers.IntegerField
        The current page number being viewed.
    page_size : serializers.IntegerField
        The number of rows per page.
    total_pages : serializers.IntegerField
        The total number of pages available based on the row count and page size.
    """

    columns = serializers.ListField(child=serializers.CharField())
    rows = serializers.ListField()
    row_count = serializers.IntegerField()
    current_page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()


class StatusOutputSerializer(serializers.Serializer):
    """
    Serializer for status output.
    Represents the status of an operation, such as file processing or enrichment.

    Attributes
    ----------
    status : serializers.CharField
        The status of the operation, e.g., "processing", "completed", "failed".
    """

    status = serializers.CharField()


class EnrichmentInputSerializer(serializers.Serializer):
    """
    Serializer for enrichment input.
    Validates the parameters required for enriching a file's content via an external API.

    Attributes
    ----------
    api_endpoint : serializers.URLField
        The URL of the external API to be used for enrichment.
    file_key : serializers.CharField
        The key mapping within the original file to be used for enrichment.
    api_key : serializers.CharField
        The key mapping within the API response to be used for enrichment.
    enriched_file_name : serializers.CharField
        The name of the enriched file to be created,
        must end with ".csv" and not already exist in the database.

    Raises
    ------
    serializers.ValidationError
        If the enriched file name does not end with ".csv" or if a file with that name already exists.
    """

    api_endpoint = serializers.URLField()
    file_key = serializers.CharField()
    api_key = serializers.CharField()
    enriched_file_name = serializers.CharField()

    def validate_enriched_file_name(self, value: str) -> str:
        """
        Validates the enriched file name to ensure it meets the following criteria:
            - The name must end with ".csv".
            - A file with the same name must not already exist in the database.

        Parameters
        ----------
        value : str
            The name of the enriched file to be validated.

        Returns
        -------
        str
            The validated enriched file name if it meets all the criteria.
        """

        if not value.endswith(".csv"):
            raise serializers.ValidationError("File name must end with .csv")

        if UploadedFile.objects.filter(original_name=value).exists():
            raise serializers.ValidationError("A file with this name already exists")

        return value
