from rest_framework import serializers

from money.models import Category, Tag, Expense


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "family",
            "title",
            "color",
            "icon",
            "limit",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = ["id", "family", "created_at", "updated_at", "deleted_at"]


class CategoryListSerializer(CategorySerializer):
    family = serializers.StringRelatedField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    deleted_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "id",
            "family",
            "title",
            "color",
            "category",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = ["id", "family", "created_at", "updated_at", "deleted_at"]


class TagListSerializer(TagSerializer):
    family = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    deleted_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            "id",
            "family",
            "category",
            "tag",
            "amount",
            "date_time",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "family",
            "date_time",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class ExpenseListSerializer(ExpenseSerializer):
    family = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    tag = serializers.StringRelatedField()
    date_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    deleted_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
