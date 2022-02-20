from django.db import models


class UserRole(models.TextChoices):
    SELLER = "seller"
    BUYER = "buyer"


class AcceptedCoins(models.IntegerChoices):
    FIVE = 5, "5"
    TEN = 10, "10"
    TWENTY = 20, "20"
    FIFTY = 50, "50"
    HUNDRED = 100, "100"
