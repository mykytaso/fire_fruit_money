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

    def validate(self, data):
        # Ensure that the category is not deleted
        if data["category"].deleted_at:
            raise serializers.ValidationError(
                {"category": "Cannot create tag for deleted category."}
            )

        return data


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

    def validate(self, data):
        # Ensure that the category is not deleted
        if data["category"].deleted_at:
            raise serializers.ValidationError(
                {"category": "Cannot create expense with deleted category."}
            )

        # Ensure that the tag is not deleted
        if data["tag"] and data["tag"].deleted_at:
            raise serializers.ValidationError(
                {"tag": "Cannot create expense with deleted tag."}
            )

        return data


class ExpenseListSerializer(ExpenseSerializer):
    family = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    tag = serializers.StringRelatedField(many=False)
    date_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    deleted_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
