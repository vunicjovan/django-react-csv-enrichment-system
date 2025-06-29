from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import HealthCheckSerializer
from .utils import BaseUtils


class HealthCheckView(APIView):
    """
    View to check the health of the system, including system info,
    database status, and Celery worker status.
    """

    renderer_classes = [JSONRenderer]

    def get(self, request: Request) -> HttpResponse:
        """
        Checks the health of the system by fetching system information,
        database status, and Celery worker status.

        Parameters
        ----------
        request : Request
            The HTTP request object.

        Returns
        -------
        HttpResponse
            A JSON response containing the health status of the system.
        """

        status = {
            "system": BaseUtils.fetch_system_info(),
            "database": BaseUtils.fetch_database_info(),
            "celery": BaseUtils.fetch_celery_info(),
        }

        serializer = HealthCheckSerializer(data=status)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)
