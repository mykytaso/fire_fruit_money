from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from users.views import CreateUserView, ManageUserView, InviteViewSet, FamilyViewSet

router = routers.DefaultRouter()
router.register("invites", InviteViewSet, basename="invites")
router.register("families", FamilyViewSet, basename="families")


urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("me/", ManageUserView.as_view(), name="me"),
    path("", include(router.urls)),
]

app_name = "users"
