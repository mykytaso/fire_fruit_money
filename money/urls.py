from django.urls import path, include
from rest_framework import routers

from money.views import CategoryViewSet, TagViewSet, ExpenseViewSet

router = routers.DefaultRouter()

router.register("category", CategoryViewSet, basename="category")
router.register("tag", TagViewSet, basename="tag")
router.register("expense", ExpenseViewSet, basename="expense")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "money"
