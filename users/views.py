from django.db import transaction
from django.db.models import Q
from rest_framework import generics, viewsets, mixins, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.decorators import action as action_decorator


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

    def get_object(self):
        return self.request.user


class FamilyViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = FamilySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Family.objects.all()
        if not user.is_staff:
            queryset = queryset.filter(members=user)
        return queryset

    @transaction.atomic
    @action_decorator(
        methods=["PUT"],
        detail=True,
        url_path="leave",
    )
    def leave_family(self, request, pk=None):
        family = self.get_object()
        user = request.user

        if not user in family.members.all():
            return Response(
                {"detail": f"{user.email} is not a member of this family."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user == family.admin:
            return Response(
                {"detail": "Admin cannot leave the family."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.family = Family.objects.get(admin=user)
        user.save()

        return Response(
            {"detail": "You successfully left the family"}, status=status.HTTP_200_OK
        )


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

    @transaction.atomic
    def perform_update(self, serializer):
        status = serializer.validated_data.get("status")

        if status == "decline":
            serializer.instance.delete()
            return

        elif status == "accept":
            sender = serializer.instance.sender
            recipient = serializer.instance.recipient

            recipient.family = sender.family
            recipient.save()

            serializer.instance.delete()
            return
