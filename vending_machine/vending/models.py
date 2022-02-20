import uuid
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from rest_framework.authtoken.models import Token
from vending.choices import UserRole
from vending.managers import CustomUserManager


def validate_multiple_of_five(value) -> None:
    if value == 0:
        raise ValidationError("Value cannot be 0")

    if value % 5 != 0:
        raise ValidationError(f"{value} is not a multiple of 5")


class User(AbstractUser, TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.SELLER)
    email = models.EmailField(null=True, blank=True)
    deposit = models.PositiveIntegerField(
        null=False, blank=False, default=0, validators=[validate_multiple_of_five]
    )
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.username


class Product(TimeStampedModel):

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(null=False, blank=False, max_length=100, unique=True, db_index=True)
    cost = models.PositiveIntegerField(
        null=False, blank=False, validators=[validate_multiple_of_five]
    )
    available_amount = models.PositiveIntegerField(null=False, blank=False)
    seller_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.name = " ".join(word.lower().capitalize() for word in self.name.split())
        return super().save(*args, **kwargs)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(
    sender: str, instance: AbstractUser = None, created: bool = False, **kwargs: Optional[dict]
) -> None:
    """
    Automatically assign a token to a user on creation
    """
    if created:
        Token.objects.create(user=instance)
