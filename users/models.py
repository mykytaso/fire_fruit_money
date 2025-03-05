from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager

from fire_fruit_money import settings
from fire_fruit_money.settings import AUTH_USER_MODEL


class UserManager(DjangoUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Family(models.Model):
    admin = models.OneToOneField(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="family_admin"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.admin}'s family"


class Invite(models.Model):
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("accept", "accept"),
        ("decline", "decline"),
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_invites"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_invites",
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "recipient"], name="unique_sender_recipient"
            ),
        ]


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_("email address"), unique=True)

    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="members",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()


@receiver(post_save, sender=get_user_model())
def create_family_for_user(sender, instance, created, **kwargs):
    if created:
        family = Family.objects.create(admin=instance)

        # Add the user to the family
        family.members.add(instance)
        family.save()

        # Update the user's family field
        instance.family = family
        instance.save()
