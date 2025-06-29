import unittest
from unittest.mock import patch, MagicMock

from ..utils import BaseUtils


class TestBaseUtils(unittest.TestCase):
    """
    Test suite for BaseUtils class methods, includes tests
    for fetching system information and database details.
    """

    @patch("psutil.virtual_memory")
    def test_fetch_memory_usage(self, mock_memory: MagicMock) -> None:
        memory_mock = MagicMock()
        memory_mock.total = 8 * (1024 ** 3)  # 8 GB
        memory_mock.available = 4 * (1024 ** 3)  # 4 GB
        memory_mock.percent = 50.0
        mock_memory.return_value = memory_mock

        system_info = BaseUtils.fetch_system_info()

        self.assertEqual(system_info["memory"]["total"], "8.00 GB")
        self.assertEqual(system_info["memory"]["available"], "4.00 GB")
        self.assertEqual(system_info["memory"]["used_percent"], "50.00%")

    @patch("psutil.disk_usage")
    def test_fetch_disk_usage(self, mock_disk: MagicMock) -> None:
        disk_mock = MagicMock()
        disk_mock.total = 100 * (1024 ** 3)  # 100 GB
        disk_mock.free = 60 * (1024 ** 3)  # 60 GB
        disk_mock.percent = 40.0
        mock_disk.return_value = disk_mock

        system_info = BaseUtils.fetch_system_info()

        self.assertEqual(system_info["disk"]["total"], "100.00 GB")
        self.assertEqual(system_info["disk"]["free"], "60.00 GB")
        self.assertEqual(system_info["disk"]["used_percent"], "40.00%")

    @patch("platform.system")
    @patch("platform.python_version")
    @patch("psutil.cpu_count")
    @patch.object(BaseUtils, "_BaseUtils__fetch_memory_usage")
    @patch.object(BaseUtils, "_BaseUtils__fetch_disk_usage")
    def test_fetch_system_info(
            self,
            mock_disk: MagicMock,
            mock_memory: MagicMock,
            mock_cpu: MagicMock,
            mock_python: MagicMock,
            mock_os: MagicMock,
    ) -> None:
        mock_os.return_value = "Linux"
        mock_python.return_value = "3.9.0"
        mock_cpu.return_value = 8
        mock_memory.return_value = {"total": "16.00 GB", "available": "8.00 GB", "used_percent": "50.00%"}
        mock_disk.return_value = {"total": "1000.00 GB", "free": "500.00 GB", "used_percent": "50.00%"}

        result = BaseUtils.fetch_system_info()

        self.assertEqual(result["os"], "Linux")
        self.assertEqual(result["python_version"], "3.9.0")
        self.assertEqual(result["cpu_count"], 8)
        self.assertEqual(result["memory"], mock_memory.return_value)
        self.assertEqual(result["disk"], mock_disk.return_value)

    @patch("django.db.connection.introspection.table_names")
    @patch("django.conf.settings.DATABASES")
    def test_fetch_database_info_success(
            self,
            mock_databases: MagicMock,
            mock_table_names: MagicMock,
    ) -> None:
        mock_table_names.return_value = ["users", "products"]
        mock_databases.__getitem__.return_value = {"ENGINE": "django.db.backends.postgresql"}

        result = BaseUtils.fetch_database_info()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["tables"], ["users", "products"])
        self.assertEqual(result["engine"], "postgresql")
