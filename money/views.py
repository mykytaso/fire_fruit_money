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


class CategoryViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = Category.objects.select_related("family")
        if not self.request.user.is_staff:
            queryset = queryset.filter(family=self.request.user.family)
        return queryset

    def get_serializer_class(self):
        return (
            CategoryListSerializer
            if self.action in ("list", "retrieve")
            else CategorySerializer
        )

    def perform_create(self, serializer):
        serializer.save(family=self.request.user.family)


class TagViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = Tag.objects.select_related("family", "category")
        if not self.request.user.is_staff:
            queryset = queryset.filter(family=self.request.user.family)
        return queryset

    def get_serializer_class(self):
        return (
            TagListSerializer if self.action in ("list", "retrieve") else TagSerializer
        )

    def perform_create(self, serializer):
        serializer.save(family=self.request.user.family)


class ExpenseViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = Expense.objects.select_related("family", "category", "tag")

        if not self.request.user.is_staff:
            queryset = queryset.filter(family=self.request.user.family)

        return queryset

    def get_serializer_class(self):
        return (
            ExpenseListSerializer
            if self.action in ("list", "retrieve")
            else ExpenseSerializer
        )

    def perform_create(self, serializer):
        serializer.save(family=self.request.user.family)
