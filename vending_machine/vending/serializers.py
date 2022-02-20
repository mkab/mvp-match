from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from vending.choices import AcceptedCoins
from vending.exceptions.exceptions import (
    InsufficientFundsException,
    ProductInsufficientStockException,
    ProductOutOfStockException,
    UnacceptableCoinExceptionException,
)
from vending.models import Product, User


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "cost", "available_amount", "seller_id")

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            raise ValidationError(e)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "deposit", "role")
        extra_kwargs = {"password": {"write_only": True}, "deposit": {"read_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class DepositSerializer(serializers.Serializer):
    deposit = serializers.IntegerField(required=True)

    def validate_deposit(self, value):
        coins = ", ".join(coin for coin in AcceptedCoins.labels)

        if value not in AcceptedCoins.values:
            raise UnacceptableCoinExceptionException(
                f"Cannot accept coin - {value} cents. " f"Accepted coins are: {coins}"
            )
        return value


class ProductBuySerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True, min_value=0)

    def validate(self, data):
        context = self.context["request"]

        try:
            product: Product = Product.objects.get(pk=data["product_id"])
        except Product.DoesNotExist:
            raise ValidationError({"product": "No such product exists."})

        purchase_amount = data["amount"]
        available_amount = product.available_amount
        total_cost = product.cost * purchase_amount

        buyer: User = context.user

        if available_amount == 0:
            raise ProductOutOfStockException(
                {"product": f"Product {product.name} is out of stock."}
            )
        elif available_amount < purchase_amount:
            raise ProductInsufficientStockException(
                {
                    "amount": (
                        "Not enough stock. "
                        f"You want to buy {purchase_amount} {product.name} "
                        f"but there is only {available_amount} available."
                    )
                }
            )
        elif buyer.deposit < total_cost:
            raise InsufficientFundsException({"buyer": f"You do not have sufficient deposit."})

        data["product"] = product
        data["total_cost"] = total_cost
        return data
