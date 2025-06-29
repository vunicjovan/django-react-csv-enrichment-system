from typing import Any, Optional

from django.core.files.base import ContentFile

from .models import UploadedFile, FileContent
from .utils import FileUtils
from ..base.enums import UploadStatus


class FileService:
    """
    Service class for handling file operations such as creation, enrichment, and preview data retrieval.
    """

    @staticmethod
    def create_file(file_obj: Any) -> Any:
        """
        Creates an UploadedFile instance from the input file object.

        Parameters
        ----------
        file_obj : Any
            The file object to be processed, typically a Django `UploadedFile` instance.

        Returns
        -------
        UploadedFile
            An instance of the UploadedFile model with the file details.
        """

        return UploadedFile.objects.create(
            file=file_obj,
            original_name=file_obj.name,
            file_size=file_obj.size,
        )

    @staticmethod
    def get_preview_data(file: Any, params: dict[str, int]) -> dict[str, Any]:
        """
        Retrieves a preview of the file content based on pagination parameters by
        extracting a subset of rows from the file content for preview purposes,
        allowing for efficient viewing of large files.

        Parameters
        ----------
        file : UploadedFile
            The UploadedFile instance containing the file content and metadata.
        params : dict[str, int]
            A dictionary containing pagination parameters:

            - "page": The current page number (1-indexed).
            - "page_size": The number of rows to display per page.

        Returns
        -------
        dict[str, Any]
            A dictionary containing the preview data, including:

            - "columns": The list of column names in the file.
            - "rows": The subset of rows for the current page.
            - "row_count": The total number of rows in the file.
            - "current_page": The current page number.
            - "page_size": The number of rows per page.
            - "total_pages": The total number of pages based on the row count and page size.
        """

        page = params["page"]
        page_size = params["page_size"]
        content = file.content

        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        return {
            "columns": file.columns,
            "rows": content.data[start_index:end_index],
            "row_count": content.row_count,
            "current_page": page,
            "page_size": page_size,
            "total_pages": (content.row_count + page_size - 1) // page_size,
        }

    @staticmethod
    def enrich_file(file: UploadedFile, enrichment_data: dict[str, str]) -> Optional[UploadedFile]:
        """
        Processes the file content, retrieves additional data from an external API
        and creates a new enriched file with the combined data.

        The original file remains unchanged.

        If the enrichment fails, the method will delete any partially created enriched file.

        If successful, it returns the newly created enriched file instance.

        Parameters
        ----------
        file : UploadedFile
            The `UploadedFile` instance to be enriched.
        enrichment_data : dict[str, str]
            A dictionary containing enrichment parameters, including:

            - "api_endpoint": The URL of the external API to fetch enrichment data.
            - "file_key": The key in the file content to match against the API data.
            - "api_key": The key used mapping against the API response.
            - "enriched_file_name": The desired name for the enriched file (must end with .csv).

        Returns
        -------
        Optional[UploadedFile]
            An instance of the `UploadedFile` model representing the enriched file if successful,
            or `None` if the enrichment fails and no file is created.
        """

        enriched_file = None

        try:
            # Process enrichment
            enriched_file_name, all_columns, enriched_data = FileUtils.enrich_content(file, enrichment_data)
            raw_csv_content = FileUtils.create_csv_content(all_columns, enriched_data)

            # Create enriched file
            enriched_file = UploadedFile.objects.create(
                original_name=enriched_file_name,
                file_size=0,
                is_enriched=True,
                parent_file=file,
                status=UploadStatus.COMPLETED.value,
                columns=all_columns,
            )

            # Save file content
            enriched_file.file.save(enriched_file_name, ContentFile(raw_csv_content))
            enriched_file.file_size = enriched_file.file.size
            enriched_file.save()

            # Create file content record
            FileContent.objects.create(file=enriched_file, data=enriched_data, row_count=len(enriched_data))

            return enriched_file

        except Exception:
            if enriched_file is not None:
                enriched_file.delete()
            raise
