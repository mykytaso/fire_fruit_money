from django.db import models

from users.models import Family


class Category(models.Model):
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name="categories"
    )
    title = models.CharField(max_length=100)
    color = models.CharField(max_length=6)
    icon = models.CharField(max_length=255)
    limit = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return self.title


class Tag(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="tags")
    title = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=6)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="tags"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return self.title


class Expense(models.Model):
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name="expenses"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="expenses"
    )
    tag = models.ManyToManyField(Tag, related_name="expenses")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_time = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.category}: {self.amount} at {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}"
