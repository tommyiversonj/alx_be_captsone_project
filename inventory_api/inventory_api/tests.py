from django.db import IntegrityError
from django.test import SimpleTestCase
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from .exceptions import exception_handler


class ExceptionHandlerTest(SimpleTestCase):
    def _context(self):
        factory = APIRequestFactory()
        return {'view': APIView(), 'request': factory.get('/'), 'args': (), 'kwargs': {}}

    def test_integrity_error_becomes_400_with_detail(self):
        response = exception_handler(IntegrityError("duplicate key"), self._context())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {"detail": "This operation violates a data integrity constraint."},
        )

    def test_list_shaped_validation_error_is_wrapped_in_detail(self):
        # This is exactly what PurchaseCreateSerializer/SaleCreateSerializer
        # produce when raising serializers.ValidationError("some message")
        # directly - DRF's default handler would return a bare list.
        response = exception_handler(
            ValidationError("A sale must have at least one item."), self._context()
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"detail": "A sale must have at least one item."})

    def test_dict_shaped_validation_error_is_left_unchanged(self):
        # Field-level validation errors are already consistent app-wide
        # and must not be rewrapped.
        response = exception_handler(
            ValidationError({"name": ["This field is required."]}), self._context()
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"name": ["This field is required."]})

    def test_other_api_exceptions_pass_through_unchanged(self):
        response = exception_handler(NotFound(), self._context())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"detail": "Not found."})
