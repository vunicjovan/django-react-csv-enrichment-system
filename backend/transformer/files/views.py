from django.core.cache import cache
from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .models import UploadedFile
from .serializers import (
    UploadedFileSerializer,
    EnrichmentInputSerializer,
    FileUploadInputSerializer,
    FilePreviewInputSerializer,
    FilePreviewOutputSerializer,
    StatusOutputSerializer,
)
from .services import FileService
from ..base.celery import process_file_content
from ..base.redis import FileStatusManager


class FileUploadViewSet(viewsets.ModelViewSet):
    """
    DRF ViewSet for handling file uploads, previews, downloads, enrichment, and status checks.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    parser_classes = (MultiPartParser, JSONParser)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Handles file uploads by validating the uploaded file, creating a new
        UploadedFile instance and processing the file content asynchronously.

        Returns the serialized data of the uploaded file upon successful creation.

        Parameters
        ----------
        request : Request
            Incoming request containing the file to be uploaded.

        Returns
        -------
        Response
            A response object containing the serialized data of the uploaded file and
            a status code indicating successful creation (HTTP 201 Created).
        """

        input_serializer = FileUploadInputSerializer(data=request.FILES)
        input_serializer.is_valid(raise_exception=True)

        file_obj = input_serializer.validated_data["file"]
        uploaded_file = FileService.create_file(file_obj)

        process_file_content(uploaded_file.id)
        serializer = self.get_serializer(uploaded_file)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Handles the deletion of a file by removing both the physical file from storage
        and the corresponding database entry.

        Returns a 204 No Content response upon successful deletion.

        Parameters
        ----------
        request : Request
            Incoming request to delete a file.

        Returns
        -------
        Response
            A response object with a status code indicating successful deletion (HTTP 204 No Content).
        """

        file_object = self.get_object()
        file_object.file.delete(save=False)  # Delete the physical file from storage
        file_object.delete()  # Delete the file entry from the database

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["GET"])
    def preview(self, request: Request, pk: int = None) -> Response:
        """
        Handles file preview requests by validating query parameters,
        retrieving the file object and returning paginated preview data.

        The preview data is cached for 15 minutes for performance reasons.

        If the data is already cached, it returns the cached data instead of processing the file again.

        Parameters
        ----------
        request : Request
            Incoming request containing query parameters for pagination.
        pk : int, optional
            The primary key of the file to preview. Defaults to None.

        Returns
        -------
        Response
            A response object containing the serialized preview data of the file.
            If the data is cached, it returns the cached data; otherwise,
            it processes the file and caches the result.
        """

        input_serializer = FilePreviewInputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)

        file = self.get_object()
        validated_data = input_serializer.validated_data
        cache_key = f"file_{pk}_{validated_data['page']}_{validated_data['page_size']}"
        cached_data = cache.get(cache_key)

        if cached_data:
            output_serializer = FilePreviewOutputSerializer(data=cached_data)
            output_serializer.is_valid()
            return Response(output_serializer.data)

        display_data = FileService.get_preview_data(file, validated_data)

        cache.set(cache_key, display_data, timeout=900)
        output_serializer = FilePreviewOutputSerializer(data=display_data)
        output_serializer.is_valid()

        return Response(output_serializer.data)

    @action(detail=True, methods=["GET"])
    def download(self, request: Request, pk: int = None) -> FileResponse:
        """
        Handles file download requests by retrieving the file object
        and returning it as a `FileResponse` object.

        The file is returned as an attachment with the original file name,
        allowing users to download the file directly from the endpoint.

        Parameters
        ----------
        request : Request
            Incoming request to download a file.
        pk : int, optional
            The primary key of the file to download. Defaults to None.

        Returns
        -------
        FileResponse
            A response object containing the file to be downloaded.
            The file is served with a content type of "text/csv" and
            the original file name as the attachment filename.
        """

        file = self.get_object()
        return FileResponse(
            file.file,
            content_type="text/csv",
            as_attachment=True,
            filename=file.original_name,
        )

    @action(detail=True, methods=["POST"])
    def enrich(self, request: Request, pk: int = None) -> Response:
        """
        Handles file enrichment requests by validating the input data,
        enriching the file with external API data, and returning the enriched file.

        Parameters
        ----------
        request : Request
            Incoming request containing the enrichment parameters.
        pk : int, optional
            The primary key of the file to be enriched. Defaults to None.

        Returns
        -------
        Response
            A response object containing the serialized data of the enriched file
            and a status code indicating successful creation (HTTP 201 Created).
        """

        serializer = EnrichmentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = self.get_object()
        enriched_file = FileService.enrich_file(file, serializer.validated_data)
        response_serializer = self.get_serializer(enriched_file)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["GET"])
    def status(self, request: Request, pk: int = None) -> Response:
        """
        Handles status check requests for a file by retrieving the processing status
        and returning it in a serialized format, allowing users to check the current
        processing status of a file, such as whether it is being processed, completed or failed.

        Parameters
        ----------
        request : Request
            Incoming request to check the status of a file.
        pk : int, optional
            The primary key of the file whose status is being checked. Defaults to None.

        Returns
        -------
        Response
            A response object containing the serialized processing status of the file.
            If the status is not found, it returns a default status of "Unknown".
        """

        processing_status = FileStatusManager.get_processing_status(pk) or {"status": "Unknown"}
        output_serializer = StatusOutputSerializer(data=processing_status)
        output_serializer.is_valid()

        return Response(output_serializer.data)
