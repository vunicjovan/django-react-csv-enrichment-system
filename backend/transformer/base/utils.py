import logging
import platform
from typing import Any

import psutil
from django.conf import settings
from django.db import connection

from .celery import app


class BaseUtils:
    """
    Utility class for fetching system, database, and Celery information.
    """

    @classmethod
    def __gb_string(cls, bytes_value: int) -> str:
        """
        Provides memory value formatted as a GB-based string.

        Parameters
        ----------
        bytes_value : int
            Memory value in bytes

        Returns
        -------
        str
            Memory value in GB in string form
        """

        value = bytes_value / (1024 ** 3) if bytes_value else 0.0
        return f"{value:.2f} GB" if value else "0.00 GB"

    @classmethod
    def __percent_string(cls, value: float) -> str:
        """
        Provides a percentage string format for the input value.

        Parameters
        ----------
        value : float
            Input value

        Returns
        -------
        str
            Percentage string for the given input value
        """

        return f"{value:.2f}%" if value is not None else "0.00%"

    @classmethod
    def __fetch_memory_usage(cls) -> dict[str, str]:
        """
        Fetches the system memory usage statistics.

        Returns
        -------
        dict
            A dictionary containing total, available memory in GB, and used percentage
        """

        memory = psutil.virtual_memory()
        return {
            "total": cls.__gb_string(memory.total),
            "available": cls.__gb_string(memory.available),
            "used_percent": cls.__percent_string(memory.percent),
        }

    @classmethod
    def __fetch_disk_usage(cls) -> dict[str, str]:
        """
        Fetches the disk usage statistics.

        Returns
        -------
        dict
            A dictionary containing total disk space, free space in GB, and used percentage
        """

        disk = psutil.disk_usage('/')
        return {
            "total": cls.__gb_string(disk.total),
            "free": cls.__gb_string(disk.free),
            "used_percent": cls.__percent_string(disk.percent),
        }

    @classmethod
    def fetch_system_info(cls) -> dict[str, Any]:
        """
        Fetches system information including OS, Python version, CPU count, memory and disk usage.

        Returns
        -------
        dict
            A dictionary containing system information such as OS, Python version, CPU count,
            memory usage statistics, and disk usage statistics.
        """

        return {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory": cls.__fetch_memory_usage(),
            "disk": cls.__fetch_disk_usage(),
        }

    @classmethod
    def fetch_database_info(cls) -> dict[str, Any]:
        """
        Fetches database connection information including status, list of tables, and engine type.

        Returns
        -------
        dict
            A dictionary containing database status, list of tables, and engine type.
        """

        db_status = {
            "status": "error",
            "tables": [],
            "engine": None,
        }

        try:
            db_status["status"] = "ok"
            db_status["tables"] = connection.introspection.table_names()
            db_status["engine"] = settings.DATABASES["default"]["ENGINE"].split(".")[-1]
        except Exception as e:
            logging.getLogger(__name__).debug(f"Database connection error: {e}")

        return db_status

    @classmethod
    def fetch_celery_info(cls) -> dict[str, Any]:
        """
        Fetches Celery information including status and registered tasks.

        Returns
        -------
        dict
            A dictionary containing Celery status and a list of registered tasks.
        """

        celery_status = {
            "status": "error",
            "registered_tasks": [],
        }

        try:
            celery_status["status"] = "ok"
            celery_status["registered_tasks"] = list(app.control.inspect().registered_tasks().values())[0]
        except Exception as e:
            logging.getLogger(__name__).debug(f"Celery connection error: {e}")

        return celery_status
