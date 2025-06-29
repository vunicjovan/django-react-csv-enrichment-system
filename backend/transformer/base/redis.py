from django.conf import settings
from redis import Redis


class FileStatusManager:
    """
    TODO
    """

    client: Redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=3,
        decode_responses=True,
    )

    @classmethod
    def get_processing_status(cls, file_id: int) -> dict:
        """
        Retrieves the processing status of a file from Redis using its file ID.

        Parameters
        ----------
        file_id : int
            The ID of the file whose processing status is to be retrieved.

        Returns
        -------
        dict
            A dictionary containing the processing status, including status, progress, and updated_at timestamp.
        """

        return cls.client.hgetall(f"file_status:{file_id}")

    @classmethod
    def set_processing_status(cls, file_id: int, status: str, progress: int = 0) -> None:
        """
        Sets the processing status of a file in Redis.

        Parameters
        ----------
        file_id : int
            The ID of the file whose processing status is to be set.
        status : str
            The current status of the file processing (e.g., "processing", "completed", "failed").
        progress : int
            The current progress of the file processing, represented as a percentage (0-100).
        """

        cls.client.hmset(
            name=f"file_status:{file_id}",
            mapping={
                "status": status,
                "progress": progress,
                "updated_at": cls.client.time()[0],
            },
        )
