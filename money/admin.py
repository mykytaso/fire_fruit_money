from django.contrib import admin

from money.models import Category, Tag, Expense

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Expense)
