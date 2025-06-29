from pathlib import Path

from django.core.files.storage import FileSystemStorage


class CSVFileStorage(FileSystemStorage):
    def get_valid_name(self, name: str) -> str:
        """
        Convert a filename to a valid format by replacing spaces with underscores
        and converting to lowercase.

        Parameters
        ----------
        name : str
            The original filename to be converted.

        Returns
        -------
        str
            A valid filename that can be used in the filesystem.
        """

        return name.replace(" ", "_").lower()  # A common defensive programming practice

    def get_available_name(self, name: str, max_length: int = None) -> str:
        """
        Generate a unique filename by appending a counter if the file already exists.
        This method checks if a file with the given name already exists in the storage.
        If it does, it appends a counter to the filename until a unique name is found.

        Parameters
        ----------
        name : str
            The original filename to check for uniqueness.
        max_length : int
            Optional maximum length for the filename. If provided, it will be used to truncate the name.

        Returns
        -------
        str
            A unique filename that does not conflict with existing files in the storage.
        """

        original_name = Path(name)
        counter = 1

        while self.exists(name):
            name = f"{original_name.stem}_{counter}{original_name.suffix}"
            counter += 1

        return name
