import logging
from typing import Any

from django.http import HttpResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware to log incoming requests and outgoing responses.
    """

    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        """
        Process the request and log the details, as well as
        the response before returning it.

        Parameters
        ----------
        request : Any
            The incoming HTTP request object.

        Returns
        -------
        Any
            The HTTP response object after processing the request.
        """

        # Log the incoming request
        logger.info(f"REQUEST: {request.method} {request.path} - Headers: {request.headers}")
        if request.body:
            logger.info(f"Request Body: {request.body}")

        response = self.get_response(request)

        # Log the outgoing response
        if isinstance(response, HttpResponse):
            logger.info(f"RESPONSE: {response.status_code}")
            if hasattr(response, "data"):
                logger.info(f"Response Data: {response.data}")

        return response
