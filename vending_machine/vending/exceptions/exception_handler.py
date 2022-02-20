from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler to first get the standard error response
    response = exception_handler(exc, context)

    # Edit the response sent for IntegrityErrors
    if not response and isinstance(exc, IntegrityError):
        return Response(
            {
                "error_message": "An error occurred while serving your request. Please review your request and try again."
            },
            status=HTTP_400_BAD_REQUEST,
        )

    return response
