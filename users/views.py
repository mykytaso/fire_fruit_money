from django.contrib.auth import get_user_model
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
        methods=["GET"],
        detail=True,
        url_path="leave",
    )
    def leave_family(self, request, pk=None):
        family = self.get_object()
        member = request.user

        if not member in family.members.all():
            return Response(
                {"detail": f"{member.email} is not a member of this family."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if member == family.admin:
            return Response(
                {"detail": "Admin cannot leave the family."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member.family = Family.objects.get(admin=member)
        member.save()

        return Response(
            {"detail": "You successfully left the family"}, status=status.HTTP_200_OK
        )

    @transaction.atomic
    @action_decorator(
        methods=["GET"],
        detail=True,
        url_path="delete",
    )
    def delete_member(self, request, pk=None):
        family = self.get_object()
        admin = request.user

        if admin != family.admin:
            return Response(
                {"detail": "Only the family admin can manage members."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member_email = self.request.query_params.get("member")

        if not member_email:
            return Response(
                {"detail": "Use parameters to delete member from family. Example: /?member=user@mail.com"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not family.members.filter(email=member_email).exists():
            return Response(
                {"detail": f"{member_email} is not a member of your family."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if member_email == admin.email:
            return Response(
                {"detail": "Admin cannot leave the family."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member = get_user_model().objects.get(email=member_email)
        member.family = Family.objects.get(admin=member)
        member.save()

        return Response(
            {"detail": f"You successfully deleted {member} from your family."},
            status=status.HTTP_200_OK,
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
        invite_status = serializer.validated_data.get("status")

        if invite_status == "decline":
            serializer.instance.delete()
            return

        elif invite_status == "accept":
            sender = serializer.instance.sender
            recipient = serializer.instance.recipient

            recipient.family = sender.family
            recipient.save()

            serializer.instance.delete()
            return
