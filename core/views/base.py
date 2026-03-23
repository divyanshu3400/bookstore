from rest_framework import viewsets
from .utils import ExceptionHandlerMixin,StandardResultsSetPagination
from rest_framework.filters import SearchFilter, OrderingFilter
import logging
logger = logging.getLogger(__name__)
class BaseModelViewSet(ExceptionHandlerMixin, viewsets.ModelViewSet):
    """
    Base reusable ViewSet providing:

    - Unified exception handling
    - SDUI-compatible success/error responses
    - Pagination, filtering, searching, ordering
    - Soft delete fallback
    - Bulk delete support
    - User hierarchy helpers

    All domain-specific ViewSets should extend this.
    """

    permission_classes = []
    pagination_class = StandardResultsSetPagination

    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = None
    ordering = None
    lookup_field = "pk"


    # -------------------------------------------------
    # LIST
    # -------------------------------------------------

    def list(self, request, *args, **kwargs):
        """
        List records with filtering, pagination and ordering.
        """
        logger.debug(
            "List request received",
            extra={
                "view": self.__class__.__name__,
                "user_id": getattr(request.user, "id", None),
            },
        )

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page or queryset, many=True)

        if page is not None:
            return self.paginator.get_paginated_response(serializer.data)

        return self.success_response(
            message="Records fetched successfully.",
            data=serializer.data,
        )

    # -------------------------------------------------
    # RETRIEVE
    # -------------------------------------------------

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single record by lookup field.
        """
        instance = self.get_object()

        logger.debug(
            "Retrieve request",
            extra={
                "view": self.__class__.__name__,
                "lookup": self.lookup_field,
                "value": getattr(instance, self.lookup_field, None),
            },
        )

        serializer = self.get_serializer(instance)
        return self.success_response(
            message="Record retrieved successfully.",
            data=serializer.data,
        )

    # -------------------------------------------------
    # CREATE
    # -------------------------------------------------

    def create(self, request, *args, **kwargs):
        """
        Create a new record.
        """
        logger.info(
            "Create request initiated",
            extra={
                "view": self.__class__.__name__,
                "user_id": getattr(request.user, "id", None),
            },
        )

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        instance = serializer.instance
        instance.refresh_from_db()

        logger.info(
            "Record created",
            extra={
                "view": self.__class__.__name__,
                "id": getattr(instance, self.lookup_field, None),
            },
        )

        response_serializer = self.get_serializer(instance)
        return self.success_response(
            message="Record created successfully.",
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    # -------------------------------------------------
    # UPDATE / PARTIAL UPDATE
    # -------------------------------------------------

    def update(self, request, *args, **kwargs):
        """
        Update an existing record (PUT / PATCH).
        """
        instance = self.get_object()

        logger.info(
            "Update request initiated",
            extra={
                "view": self.__class__.__name__,
                "id": getattr(instance, self.lookup_field, None),
                "partial": kwargs.get("partial", False),
            },
        )

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=kwargs.get("partial", False),
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        instance.refresh_from_db()

        logger.info(
            "Record updated",
            extra={
                "view": self.__class__.__name__,
                "id": getattr(instance, self.lookup_field, None),
            },
        )

        response_serializer = self.get_serializer(instance)
        return self.success_response(
            message="Record updated successfully.",
            data=response_serializer.data,
        )

    # -------------------------------------------------
    # DELETE (Soft delete aware)
    # -------------------------------------------------

    def destroy(self, request, *args, **kwargs):
        """
        Delete a record.
        Uses soft delete if available.
        """
        instance = self.get_object()

        logger.warning(
            "Delete request initiated",
            extra={
                "view": self.__class__.__name__,
                "id": getattr(instance, self.lookup_field, None),
                "user_id": getattr(request.user, "id", None),
            },
        )

        if hasattr(instance, "soft_delete") and callable(instance.soft_delete):
            instance.soft_delete()
            delete_type = "soft"
        else:
            instance.delete()
            delete_type = "hard"

        logger.warning(
            "Record deleted",
            extra={
                "view": self.__class__.__name__,
                "id": getattr(instance, self.lookup_field, None),
                "delete_type": delete_type,
            },
        )

        return self.success_response(
            message="Record deleted successfully.",
            data=None,
        )
