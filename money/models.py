from django.db import models

from users.models import Family


class Category(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name="categories"
    )
    title = models.CharField(max_length=100)
    color = models.CharField(max_length=6)
    icon = models.CharField(max_length=255)
    limit = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.title


class Tag(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="tags")
    title = models.CharField(max_length=100)
    color = models.CharField(max_length=6)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="tags"
    )

    def __str__(self):
        return self.title


class Expense(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name="expenses"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="expenses"
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, blank=True, null=True, related_name="expenses"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category}: {self.amount} at {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}"
