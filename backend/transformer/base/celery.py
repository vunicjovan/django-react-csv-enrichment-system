import csv
import logging
import os

from celery import Celery
from celery.exceptions import MaxRetriesExceededError
from django.apps import apps

from .enums import UploadStatus
from .redis import FileStatusManager

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transformer.settings")

app = Celery("transformer")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_file_content(self, file_id: int) -> bool:
    """
    Reads the CSV file with the given ID, processes its content
    and updates the status of the file in the database.

    Handles errors and retries up to three times if necessary.

    Parameters
    ----------
    self : celery.Task
        The current task instance.
    file_id : int
        The ID of the file to be processed.

    Returns
    -------
    bool
        True if the file was processed successfully, otherwise False.
    """

    logger = logging.getLogger(__name__)

    try:
        # Get the UploadedFile and FileContent models from the apps registry to avoid circular imports
        UploadedFile = apps.get_model("transformer", "UploadedFile")
        FileContent = apps.get_model("transformer", "FileContent")

        # Retrieve the file and set its status to processing (initial phase)
        uploaded_file = UploadedFile.objects.get(id=file_id)
        FileStatusManager.set_processing_status(file_id, UploadStatus.PROCESSING.value, 0)

        try:
            # Read the content of the uploaded file
            content = uploaded_file.file.read().decode("utf-8")
            csv_reader = csv.DictReader(content.splitlines())
            columns = csv_reader.fieldnames
            rows = []

            # Process rows with progress tracking, updating status on every 1000 rows
            for i, row in enumerate(csv_reader):
                rows.append(row)
                if i % 1000 == 0:  # Update progress every 1000 rows
                    progress = int((i / uploaded_file.file_size) * 100)
                    FileStatusManager.set_processing_status(file_id, UploadStatus.PROCESSING.value, progress)

            # Finalize the processing of the file by updating the status and saving the content
            uploaded_file.columns = columns
            uploaded_file.status = UploadStatus.COMPLETED.value
            uploaded_file.save()

            FileContent.objects.create(file=uploaded_file, data=rows, row_count=len(rows))
            FileStatusManager.set_processing_status(file_id, UploadStatus.COMPLETED.value, 100)

            return True
        except UploadedFile.DoesNotExist as e:
            # Handle the case where the file does not exist
            logger.error(f"File {file_id} not found: {str(e)}")
            return False
        except Exception as e:
            # Handle any other exceptions that occur during file processing by triggering the retry mechanism
            uploaded_file.status = UploadStatus.FAILED.value
            uploaded_file.save()
            FileStatusManager.set_processing_status(file_id, UploadStatus.FAILED.value, 0)
            logger.error(f"Error processing file {file_id}: {str(e)}")
            raise e
    except Exception as e:
        # If an error occurs, log it and retry the task, or fail after max retries
        try:
            self.retry(exc=e)
            return False
        except MaxRetriesExceededError as e:
            FileStatusManager.set_processing_status(file_id, UploadStatus.FAILED.value, 0)
            logger.error(f"Error processing file {file_id} after max retries: {str(e)}")
            return False
