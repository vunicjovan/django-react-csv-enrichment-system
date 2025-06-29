from enum import Enum


class BaseEnum(Enum):
    """
    Base class for all enums in the application.
    """

    def __str__(self) -> str:
        return self.value

    @classmethod
    def values(cls) -> list[str]:
        """
        Returns a list of all values in the enum.

        Returns
        -------
        list[str]
            A list of string values corresponding to the enum members.
        """

        return [member.value for member in cls]


class SizeUnit(BaseEnum):
    """
    Enum representing different size units for file sizes.
    """

    BYTE = "B"
    KILOBYTE = "KB"
    MEGABYTE = "MB"


class UploadStatus(BaseEnum):
    """
    Enum representing the status of file uploads.
    """

    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """
        Returns a list of tuples representing the choices for the upload status.

        Returns
        -------
        list[tuple[str, str]]
            A list of tuples where each tuple contains the value and label of the enum member.
        """

        return [(member.value, member.value) for member in cls]
