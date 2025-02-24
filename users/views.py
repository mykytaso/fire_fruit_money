from django.db.models import Q
from rest_framework import generics, viewsets, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.settings import api_settings

from users.models import Invite, Family
from users.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    InviteSerializer,
    InviteListSerializer,
    InviteUpdateSerializer,
    FamilySerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = ()


class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class FamilyViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    permission_classes = (IsAdminUser,)
    serializer_class = FamilySerializer
    queryset = Family.objects.all()


class InviteViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        queryset = Invite.objects.select_related("sender", "recipient")
        if not user.is_staff:
            queryset = queryset.filter(Q(sender=user) | Q(recipient=user))
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return InviteListSerializer

        if self.action in ("update", "partial_update"):
            return InviteUpdateSerializer

        return InviteSerializer

    #
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def perform_update(self, serializer):
        status = serializer.validated_data.get("status")

        if status == "decline":
            serializer.instance.delete()
            return

        elif status == "accept":
            sender = serializer.instance.sender
            recipient = serializer.instance.recipient

            sender_family = sender.family
            recipient_family = recipient.family

            recipient.family = sender_family
            recipient.save()

            recipient_family.delete()
            serializer.instance.delete()
            return
