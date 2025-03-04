from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.relations import StringRelatedField

from users.models import Invite, User, Family


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "is_staff",
        )
        read_only_fields = (
            "id",
            "is_staff",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "style": {"input_type": "password"},
                "label": _("Password"),
            },
        }

    def create(self, validated_data):
        """ "create useer with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update user with encrypted password"""

        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _("Must include 'email' and 'password'.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class FamilySerializer(serializers.ModelSerializer):
    admin = StringRelatedField(many=False, read_only=True)
    members = StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Family
        fields = ["id", "admin", "members"]


class InviteSerializer(serializers.ModelSerializer):
    recipient = serializers.CharField(write_only=True)

    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Invite
        fields = ["id", "sender", "recipient", "status", "created_at", "updated_at"]
        read_only_fields = ("id", "sender", "status", "created_at", "updated_at")

    def validate(self, data):
        sender = self.context["request"].user

        # Trying to find the recipient among users in the database
        try:
            recipient = User.objects.get(email=data.get("recipient"))
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"recipient": "User with this email does not exist."}
            )

        # Ensure the sender is not inviting themselves
        if sender == recipient:
            raise serializers.ValidationError(
                {"recipient": "You cannot invite yourself to your own family."}
            )

        # Ensure that an invitation between the sender and recipient does not already exist
        if Invite.objects.filter(sender=sender, recipient=recipient).exists():
            raise serializers.ValidationError(
                {"recipient": "You have already sent an invite to this user."}
            )

        # Ensure that the recipient has not already sent an invitation to the sender
        if Invite.objects.filter(sender=recipient, recipient=sender).exists():
            raise serializers.ValidationError(
                {
                    "recipient": f"{recipient.email} has already sent you invitation to join their family."
                }
            )

        # Ensure thar recipient doesn't have any member in their family
        if recipient.family.members.count() > 1:
            raise serializers.ValidationError(
                {"recipient": f"{recipient.email} has family with multiple members."}
            )

        data["recipient"] = recipient
        return data


class InviteListSerializer(InviteSerializer):
    sender = serializers.StringRelatedField()
    recipient = serializers.StringRelatedField()


class InviteUpdateSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()
    recipient = serializers.StringRelatedField()

    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Invite
        fields = ["id", "sender", "recipient", "status", "created_at", "updated_at"]
        read_only_fields = ("id", "sender", "recipient", "created_at", "updated_at")
