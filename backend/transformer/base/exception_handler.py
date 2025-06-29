import logging
import traceback

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: dict) -> Response:
    """
    Custom exception handler for DRF to log exceptions and return a standardized error response.
    This is useful for logging exceptions in a consistent manner and ensuring that the API
    returns a user-friendly error message to front-end client.

    Parameters
    ----------
    exc : Exception
        The exception that was raised.
    context : dict
        The context in which the exception occurred, typically containing the request and view information.

    Returns
    -------
    Response
        A DRF Response object containing the error message and appropriate HTTP status code.
        If the exception is not handled, it returns a generic error message with a 400 status code.
    """

    # Log the exception
    logger.error(f"Exception in {context['request'].method} {context['request'].path}")
    logger.error(traceback.format_exc())

    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    # If response is None, handle the exception generically
    if response is None:
        response = Response(data={"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    # Format any DRF-handled exceptions
    elif hasattr(response, "data"):
        if isinstance(response.data, dict):
            # Extract first error message from any field
            for field, errors in response.data.items():
                if isinstance(errors, (list, tuple)):
                    error_message = errors[0]
                else:
                    error_message = errors

                response.data = {"error": str(error_message)}

                break

    return response
