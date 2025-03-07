from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from money.models import Category, Tag, Expense
from money.serializers import (
    CategorySerializer,
    CategoryListSerializer,
    TagSerializer,
    TagListSerializer,
    ExpenseListSerializer,
    ExpenseSerializer,
)


class BaseMoneyViewSet(viewsets.ModelViewSet):
    """A base ViewSet that provides common functionality for money-related views."""

    def queryset_last_sync_time_filter(self, queryset):
        last_sync_time = self.request.query_params.get("last_sync_time")
        if last_sync_time:
            queryset = queryset.filter(updated_at__gte=last_sync_time)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="last_sync_time",
                type=str,
                description="Filter by last sync time in ISO 8601 format. Example: `?last_sync_time=2025-01-02T14:05:21Z` (UTC).",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CategoryViewSet(BaseMoneyViewSet):
    def get_queryset(self):
        queryset = Category.objects.select_related("family")
        if not self.request.user.is_staff:
            queryset = queryset.filter(family=self.request.user.family)

        queryset = self.queryset_last_sync_time_filter(queryset)

        return queryset

    def get_serializer_class(self):
        return (
            CategoryListSerializer
            if self.action in ("list", "retrieve")
            else CategorySerializer
        )

    def perform_create(self, serializer):
        serializer.save(family=self.request.user.family)

    @transaction.atomic
    def perform_destroy(self, instance):
        tags = instance.tags.all()
        expenses = instance.expenses.all()

        if expenses:
            for expense in expenses:
                expense.deleted_at = timezone.now()
                expense.save()

        if tags:
            for tag in tags:
                tag.deleted_at = timezone.now()
                tag.save()

        instance.deleted_at = timezone.now()
        instance.save()


class TagViewSet(BaseMoneyViewSet):
    def get_queryset(self):
        queryset = Tag.objects.select_related("family", "category")
        if not self.request.user.is_staff:
            queryset = queryset.filter(family=self.request.user.family)

        queryset = self.queryset_last_sync_time_filter(queryset)

        return queryset

    def get_serializer_class(self):
        return (
            TagListSerializer if self.action in ("list", "retrieve") else TagSerializer
        )

    def perform_create(self, serializer):
        serializer.save(family=self.request.user.family)

    @transaction.atomic
    def perform_destroy(self, instance):
        expenses = instance.expenses.all()

        if expenses:
            for expense in expenses:
                expense.tag = None
                expense.updated_at = timezone.now()
                expense.save()

        instance.deleted_at = timezone.now()
        instance.save()


class ExpenseViewSet(BaseMoneyViewSet):
    def get_queryset(self):
        queryset = Expense.objects.select_related(
            "family", "category"
        ).prefetch_related("tag")

        if not self.request.user.is_staff:
            queryset = queryset.filter(family=self.request.user.family)

        queryset = self.queryset_last_sync_time_filter(queryset)

        return queryset

    def get_serializer_class(self):
        return (
            ExpenseListSerializer
            if self.action in ("list", "retrieve")
            else ExpenseSerializer
        )

    def perform_create(self, serializer):
        serializer.save(family=self.request.user.family)

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save()
