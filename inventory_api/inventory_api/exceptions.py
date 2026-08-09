from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    if isinstance(exc, IntegrityError):
        return Response(
            {"detail": "This operation violates a data integrity constraint."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    response = drf_exception_handler(exc, context)
    if response is not None and isinstance(response.data, list):
        detail = response.data[0] if len(response.data) == 1 else response.data
        response.data = {"detail": detail}
    return response
