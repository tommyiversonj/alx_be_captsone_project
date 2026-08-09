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


class OpenAPISchemaTest(SimpleTestCase):
    """
    Generates the real OpenAPI schema the same way `manage.py spectacular
    --fail-on-warn --validate` does, so schema drift (a view drf-spectacular
    can't introspect, an endpoint missing from the schema entirely) is
    caught by the test suite instead of only being discoverable by manually
    running the management command.
    """

    def test_schema_generates_without_warnings_and_is_structurally_valid(self):
        from drf_spectacular.drainage import GENERATOR_STATS
        from drf_spectacular.generators import SchemaGenerator
        from drf_spectacular.validation import validate_schema

        GENERATOR_STATS.reset()
        schema = SchemaGenerator().get_schema(request=None, public=True)

        self.assertFalse(
            bool(GENERATOR_STATS),
            "Schema generation produced warnings/errors - run "
            "`manage.py spectacular --fail-on-warn` locally to see them.",
        )
        validate_schema(schema)  # raises if the schema isn't valid OpenAPI 3

    def test_schema_includes_the_dashboard_endpoints(self):
        from drf_spectacular.generators import SchemaGenerator

        schema = SchemaGenerator().get_schema(request=None, public=True)
        for path in (
            '/api/dashboard/low-stock/',
            '/api/dashboard/total-sales/',
            '/api/dashboard/top-products/',
        ):
            self.assertIn(path, schema['paths'])
