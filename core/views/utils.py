from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from functools import wraps
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
    ObjectDoesNotExist,
)
from django.http import Http404
from django.db import IntegrityError, DatabaseError, transaction
from rest_framework.exceptions import (
    APIException,
    ValidationError as DRFValidationError,
    NotFound,
    PermissionDenied,
)
import logging

logger = logging.getLogger(__name__)

from math import ceil


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    # Optional: Attach extra data externally before calling pagination
    extra_data = {}

    def get_paginated_response(self, data):
        total_items = self.page.paginator.count
        current_page = self.page.number
        per_page = self.page.paginator.per_page
        total_pages = ceil(total_items / int(per_page))

        base_response = {
            "count": total_items,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "current_page": current_page,
            "total_pages": total_pages,
            "page_size": int(per_page),
            "has_next": self.page.has_next(),
            "has_previous": self.page.has_previous(),
            "results": data,
        }

        # Merge extra dynamic data if any
        base_response.update(self.extra_data)

        return custom_response(
            status_text="success",
            message="Success",
            data=base_response,
            status_code=status.HTTP_200_OK,
        )


def custom_response(status_text, data=None, message=None, errors=None, status_code=200):
    return Response(
        {
            "status": status_text,
            "message": message or "Success",
            "data": data,
            "errors": errors,
        },
        status=status_code,
    )


def handle_custom_exceptions():
    """
    Universal decorator to catch and handle all common exceptions
    for both function-based and class-based views.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(*args, **kwargs):
            try:
                return view_func(*args, **kwargs)

            # Common Django ORM exception
            except ObjectDoesNotExist:
                return Response(
                    {"status": "error", "message": "Requested object not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # DRF NotFound exception
            except NotFound as e:
                return Response(
                    {"status": "error", "message": str(e) or "Resource not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Integrity / constraint violations
            except IntegrityError as e:
                logger.exception("Database integrity error")
                return Response(
                    {
                        "status": "error",
                        "message": "Database integrity constraint violated.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validation exceptions (both DRF & Django)
            except (DRFValidationError, DjangoValidationError) as e:
                return Response(
                    {
                        "status": "error",
                        "message": e.message if hasattr(e, "message") else str(e),
                        "errors": getattr(e, "detail", None),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Permission issues
            except PermissionDenied as e:
                return Response(
                    {
                        "status": "error",
                        "message": str(e)
                        or "You do not have permission to perform this action.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Any other uncaught exceptions
            except Exception as e:
                logger.exception("Unexpected server error")
                return Response(
                    {"status": "error", "message": "An unexpected error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return _wrapped_view

    return decorator


from rest_framework.views import exception_handler as drf_exception_handler

from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
)
from rest_framework.views import exception_handler as drf_exception_handler


class ExceptionHandlerMixin:
    default_error_message = "An unexpected error occurred."

    def success_response(
        self, message="Success", data=None, status_code=status.HTTP_200_OK
    ):
        return custom_response(
            status_text="success",
            message=message,
            data=data if data is not None else {},
            status_code=status_code,
        )

    def error_response(
        self, message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST
    ):
        payload = {
            "status_text": "error",
            "message": message,
            "status_code": status_code,
        }
        if errors is not None:
            payload["errors"] = errors
        return custom_response(**payload)

    def handle_exception(self, exc):
        """
        Centralized exception handling for all ViewSets using this mixin
        """
        # ---- DRF native exceptions ----
        if isinstance(exc, ValidationError):
            return self.error_response(
                message="Validation error",
                errors=exc.detail,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if isinstance(exc, IntegrityError):
            return self.error_response(
                message="Database integrity error",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if isinstance(exc, NotAuthenticated):
            return self.error_response(
                message="Authentication required",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if isinstance(exc, PermissionDenied):
            return self.error_response(
                message="You do not have permission to perform this action",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if isinstance(exc, NotFound):
            return self.error_response(
                message="Resource not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # ---- Let DRF handle known exceptions first ----
        response = drf_exception_handler(exc, self.get_exception_handler_context())
        if response is not None:
            return custom_response(
                status_text="error",
                message="Request failed",
                errors=response.data,
                status_code=response.status_code,
            )

        # ---- Fallback (500) ----
        return self.error_response(
            message=self.default_error_message,
            errors={"detail": str(exc)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ResponseMixin:
    """Mixin for standardized API responses"""

    def success_response(
        self, data=None, message="Success", status_code=status.HTTP_200_OK
    ):
        """Return standardized success response"""
        return custom_response(
            data=data,
            status_text="success",
            status_code=status_code,
            message=message,
        )

    def error_response(
        self, message="Error", status_code=status.HTTP_400_BAD_REQUEST, errors=None
    ):
        """Return standardized error response"""
        return custom_response(
            data={},
            status_text="error",
            status_code=status_code,
            message=message,
            errors=errors,
        )
