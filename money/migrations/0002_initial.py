# Generated by Django 5.1.6 on 2025-02-21 22:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("money", "0001_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="family",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="categories",
                to="users.family",
            ),
        ),
        migrations.AddField(
            model_name="expense",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="expenses",
                to="money.category",
            ),
        ),
        migrations.AddField(
            model_name="expense",
            name="family",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="expenses",
                to="users.family",
            ),
        ),
        migrations.AddField(
            model_name="tag",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tags",
                to="money.category",
            ),
        ),
        migrations.AddField(
            model_name="tag",
            name="family",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tags",
                to="users.family",
            ),
        ),
        migrations.AddField(
            model_name="expense",
            name="tag",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="expenses",
                to="money.tag",
            ),
        ),
    ]
