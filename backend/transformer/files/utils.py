import csv
from io import StringIO
from typing import Any

import requests


class FileUtils:
    """
    Utility class for handling file operations, including:
        - Flattening nested JSON structures
        - Calling external APIs to enrich file data
        - Enriching file content with API data
        - Creating CSV content from enriched data
    """

    @classmethod
    def __flatten_json(
            cls,
            nested_json: dict[str, Any],
            parent_key: str = "",
            separator: str = "_"
    ) -> dict[str, Any]:
        """
        Recursively flattens a nested JSON structure into a single-level dictionary
        with keys representing the path to each value, separated by the specified separator.

        This is useful for transforming complex JSON data into a more manageable format,
        especially when preparing data for CSV output or API integration.

        Parameters
        ----------
        nested_json : dict[str, Any]
            The nested JSON structure to flatten.
        parent_key : str, optional
            The base key to prepend to each flattened key. Defaults to an empty string.
        separator : str, optional
            The string used to separate keys in the flattened structure. Defaults to an underscore ("_").

        Returns
        -------
        dict[str, Any]
            A flattened dictionary where keys are the paths to the original values in the nested JSON.
        """

        items = []

        for key, value in nested_json.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key

            if isinstance(value, dict):
                items.extend(cls.__flatten_json(value, new_key, separator).items())
            else:
                items.append((new_key, value))

        return dict(items)

    @classmethod
    def call_external_api(
            cls,
            api_endpoint: str,
            api_key: str,
            file_key: str,
            file_columns: set[str],
    ) -> tuple[set[str], dict[str, Any]]:
        """
        Retrieves data from the specified external API endpoint, validates the response,
        and prepares a lookup dictionary for enriching file content based on the specified key.

        The API response is expected to be a list of dictionaries, where each dictionary
        should contain the specified `api_key`.

        Further, collects all possible column names from the API response,
        sanitizes them, and returns a set of these column names along with a lookup
        dictionary that maps the `api_key` values to their corresponding data.
        This is useful for enriching file content with additional data from external sources,
        such as databases or web services.

        Parameters
        ----------
        api_endpoint : str
            The URL of the external API endpoint to call.
        api_key : str
            The key in the API response that will be used to match with the file content.
        file_key : str
            The key in the file content that corresponds to the `api_key` in the API response.
        file_columns : set[str]
            A set of column names from the file content to be used for enrichment.

        Returns
        -------
        tuple[set[str], dict[str, Any]]
            A tuple containing:

                - A set of column names from the API response that can be used to enrich the file content.
                - A lookup dictionary mapping the `api_key` values to their corresponding data from the API response.
        """

        response = requests.get(api_endpoint)
        assert response.ok, f"External API call failed with status code {response.status_code}: {response.text}"
        api_data = response.json()

        # Validate API response format and key
        assert isinstance(api_data, list), "API response must be a list of objects"
        assert api_data, "API response data is empty"
        assert isinstance(api_data[0], dict), "API response data must be a list of dictionaries"
        assert api_key in api_data[0], f"API response data must contain the key '{api_key}'"

        # Create lookup dictionary from API data using the api_key values
        api_data = list(map(cls.__flatten_json, api_data))  # Flatten nested JSON if needed
        api_lookup = {str(item[api_key]): item for item in api_data}

        # Collect and sanitize all possible column names from API data
        api_columns = set()

        for item in api_data:
            for key in item.keys():
                # Skip the key used for matching if it's already in original columns
                if key == api_key and file_key in file_columns:
                    continue

                # Sanitize column name
                sanitized_key = str(key).strip()

                if sanitized_key:  # Only add non-empty, sanitized keys
                    api_columns.add(sanitized_key)

        return api_columns, api_lookup

    @classmethod
    def enrich_content(cls, file: Any, enrichment_input: dict[str, str]) -> tuple[
        str,
        list[str],
        list[dict[str, Any]],
    ]:
        """
        Enriches the content of a file by calling an external API and merging the API response
        with the file's existing data. The enrichment is based on specified keys that
        exist in both the file and the API response, respectively.

        The mechanism retrieves the file's columns, validates that the specified key exists,
        and then calls the external API to fetch additional data. It combines the file's
        columns with the API response, ensuring that all columns are included in the final
        enriched data. The enriched data is returned as a list of dictionaries, where each
        dictionary represents a row with all columns initialized to `None` if no data is available
        for that column. If a match is found in the API response, the corresponding data
        is added to the enriched row.

        Parameters
        ----------
        file : Any
            The file object containing the original data, which should have a `columns` attribute
        enrichment_input : dict[str, str]
            A dictionary containing the parameters for enrichment, including:

                - `api_endpoint`: The URL of the external API to call
                - `file_key`: The key in the file content that corresponds to the API response
                - `api_key`: The key in the API response used for matching with the file content
                - `enriched_file_name`: The name of the enriched file to be created

        Returns
        -------
        tuple[str, list[str], list[dict[str, Any]]]
            A tuple containing:

                - The name of the enriched file
                - A list of all columns (from both file and API response - combined and deduplicated)
                - A list of dictionaries representing the enriched data, where each dictionary
                  contains combined columns with values from the file and API response
        """

        # Extract enrichment parameters
        api_endpoint = enrichment_input["api_endpoint"]
        file_key = enrichment_input["file_key"]
        api_key = enrichment_input["api_key"]
        enriched_file_name = enrichment_input["enriched_file_name"]

        # Fetch file columns and validate file_key exists in file columns
        file_columns = set(file.columns)
        assert file_key in file.columns, f"Column '{file_key}' not found in file columns: {file.columns}"

        # Fetch data (columns + lookup response) from external API
        api_columns, api_lookup = cls.call_external_api(api_endpoint, api_key, file_key, file_columns)

        # Combine and deduplicate columns between file and API response and extract file content
        all_columns = list(file_columns | api_columns)
        file_content = file.content.data

        # Initialize enriched data list
        enriched_data = []

        for row in file_content:
            # Create a new row with all columns initialized to None
            enriched_row = {col: None for col in all_columns}

            # Copy original data
            for col in file_columns:
                enriched_row[col] = row.get(col)

            # Add API data if there's a match
            file_key_value = str(row.get(file_key, ""))
            if file_key_value in api_lookup:
                api_row = api_lookup[file_key_value]
                for col in api_columns:
                    if col in api_row:
                        enriched_row[col] = api_row[col]

            enriched_data.append(enriched_row)

        return enriched_file_name, all_columns, enriched_data

    @classmethod
    def create_csv_content(cls, columns: list[str], data: list[dict[str, Any]]) -> bytes:
        """
        Creates a CSV content based on the provided columns and data rows.

        Parameters
        ----------
        columns : list[str]
            A list of column names to be used as headers in the CSV file.
        data : list[dict[str, Any]]
            A list of dictionaries where each dictionary represents a row of data.
            The keys in the dictionaries should match the column names.

        Returns
        -------
        bytes
            The CSV content as a byte string, ready to be written to a file or returned in a response.
        """

        with StringIO() as output:  # type: StringIO
            writer = csv.DictWriter(output, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)

            return output.getvalue().encode()
