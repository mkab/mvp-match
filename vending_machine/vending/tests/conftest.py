import pytest
from rest_framework.test import APIRequestFactory
from vending.choices import UserRole
from vending.models import Product, User


@pytest.fixture
def request_factory():
    return APIRequestFactory()


@pytest.fixture
def buyer_1():
    return User.objects.create(username="max", password="max", role=UserRole.BUYER)


@pytest.fixture
def buyer_2():
    return User.objects.create(username="jane", password="jane", role=UserRole.BUYER)


@pytest.fixture
def seller_1():
    return User.objects.create(username="tom", password="tom", role=UserRole.SELLER)


@pytest.fixture
def seller_2():
    return User.objects.create(username="mary", password="mary", role=UserRole.SELLER)


@pytest.fixture
def product_1(seller_1):
    return Product.objects.create(
        name="orange juice", cost=5, available_amount=60, seller_id=seller_1
    )


@pytest.fixture
def product_2(seller_2):
    return Product.objects.create(
        name="Kinder Bueno", cost=10, available_amount=10, seller_id=seller_2
    )
