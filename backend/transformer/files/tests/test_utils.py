import unittest
from unittest.mock import patch, MagicMock

from ..utils import FileUtils


class TestFileUtils(unittest.TestCase):
    """
    Test suite for FileUtils class methods, includes tests
    for calling external APIs, enriching content, and creating CSV content.
    """

    @patch("requests.get")
    def test_call_external_api(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = [
            {"id": "1", "name": "Product A", "price": 10.99},
            {"id": "2", "name": "Product B", "price": 20.50},
        ]
        mock_get.return_value = mock_response

        api_columns, api_lookup = FileUtils.call_external_api(
            api_endpoint="https://api.example.com/products",
            api_key="id",
            file_key="product_id",
            file_columns={"product_id", "quantity"},
        )

        self.assertEqual(api_columns, {"name", "price"})
        self.assertEqual(len(api_lookup), 2)
        self.assertEqual(api_lookup["1"]["name"], "Product A")
        self.assertEqual(api_lookup["2"]["price"], 20.50)

    @patch("requests.get")
    def test_call_external_api_error(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        with self.assertRaises(AssertionError):
            FileUtils.call_external_api(
                api_endpoint="https://api.example.com/invalid",
                api_key="id",
                file_key="product_id",
                file_columns={"product_id"},
            )

    @patch.object(FileUtils, "call_external_api")
    def test_enrich_content(self, mock_call_api: MagicMock) -> None:
        file_mock = MagicMock()
        file_mock.columns = ["product_id", "quantity"]
        file_mock.content.data = [
            {"product_id": "1", "quantity": 5},
            {"product_id": "2", "quantity": 3},
            {"product_id": "3", "quantity": 2},
        ]

        api_columns = {"name", "price"}
        api_lookup = {
            "1": {"id": "1", "name": "Product A", "price": 10.99},
            "2": {"id": "2", "name": "Product B", "price": 20.50},
        }
        mock_call_api.return_value = (api_columns, api_lookup)

        enrichment_input = {
            "api_endpoint": "https://api.example.com/products",
            "file_key": "product_id",
            "api_key": "id",
            "enriched_file_name": "enriched_products.csv",
        }

        file_name, columns, data = FileUtils.enrich_content(file_mock, enrichment_input)

        self.assertEqual(file_name, "enriched_products.csv")
        self.assertEqual(set(columns), {"product_id", "quantity", "name", "price"})
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["name"], "Product A")
        self.assertEqual(data[0]["price"], 10.99)
        self.assertEqual(data[2]["name"], None)  # No match for product_id 3

    def test_create_csv_content(self):
        columns = ["id", "name", "price"]
        data = [
            {"id": 1, "name": "Product A", "price": 10.99},
            {"id": 2, "name": "Product B", "price": 20.50},
        ]

        csv_content = FileUtils.create_csv_content(columns, data)

        csv_string = csv_content.decode("utf-8")

        expected_lines = [
            "id,name,price",
            "1,Product A,10.99",
            "2,Product B,20.5",
        ]
        csv_lines = csv_string.strip().split("\r\n")
        self.assertEqual(csv_lines, expected_lines)
