import json

import pytest
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from vending.models import Product, User
from vending.views import ProductViewSet


@pytest.mark.django_db
class TestProduct:
    def send_request(
        self,
        rf: APIRequestFactory,
        data: str,
        user: User,
        method: str,
        action: str,
        authenticate_user: bool = True,
    ) -> Response:
        if method == "post":
            endpoint = f"/vending-machine/product/"
            pk = None
        else:
            endpoint = f"/vending-machine/product/1/"
            pk = 1

        data = json.dumps(data)
        data, content_type = rf._encode_data(data, None, content_type="application/json")
        request = rf.generic(method, endpoint, data=data, content_type=content_type)

        if authenticate_user:
            force_authenticate(request, user=user)

        view = ProductViewSet.as_view({method: action})
        response = view(request, pk=pk)

        return response

    def test_get_product(self, product_1, product_2, seller_1, buyer_1, request_factory):
        # seller can get products without authenticating
        response = self.send_request(
            request_factory, None, seller_1, "get", "list", authenticate_user=False
        )
        assert response.status_code == 200

        data = response.data
        assert len(data) == 2  # we have two products

        # buyer can get products without authenticating
        response = self.send_request(
            request_factory, None, buyer_1, "get", "list", authenticate_user=False
        )
        assert response.status_code == 200

        data = response.data
        assert len(data) == 2  # we have two products

    def test_create_product_success(self, seller_1, request_factory):
        data = {"name": "test product", "cost": 100, "available_amount": 86}

        assert Product.objects.count() == 0

        response = self.send_request(request_factory, data, seller_1, "post", "create")
        assert response.status_code == 201

        assert Product.objects.count() == 1

        product = Product.objects.first()
        assert product.name == "Test Product"
        assert product.cost == 100
        assert product.available_amount == 86
        assert product.seller_id == seller_1

    def test_create_product_without_authenticating(self, seller_1, request_factory):
        data = {"name": "test product", "cost": 100, "available_amount": 86}

        assert Product.objects.count() == 0

        response = self.send_request(
            request_factory, data, seller_1, "post", "create", authenticate_user=False
        )
        assert response.status_code == 401

        error = response.data["detail"]
        assert error.code == "not_authenticated"

        assert Product.objects.count() == 0  # no products have been created

    def test_update_product_success(self, seller_1, request_factory):
        data = {"name": "test product", "cost": 100, "available_amount": 86}

        assert Product.objects.count() == 0

        # seller 1 creates product
        response = self.send_request(request_factory, data, seller_1, "post", "create")
        assert response.status_code == 201

        assert Product.objects.count() == 1

        # seller 1 modifies product
        data["cost"] = 50
        data["available_amount"] = 10
        response = self.send_request(request_factory, data, seller_1, "put", "update")
        assert response.status_code == 200

        product = Product.objects.first()
        assert product.cost == 50
        assert product.available_amount == 10

    def test_seller_cannot_modify_product_of_another_seller(
        self, seller_1, seller_2, request_factory
    ):
        data = {"name": "test product", "cost": 100, "available_amount": 86}

        assert Product.objects.count() == 0

        # seller 1 creates product
        response = self.send_request(request_factory, data, seller_1, "post", "create")
        assert response.status_code == 201

        assert Product.objects.count() == 1

        # seller 2 attempts to modify seller 1 product
        response = self.send_request(request_factory, data, seller_2, "put", "update")
        assert response.status_code == 403

        error = response.data["detail"]
        assert error.code == "permission_denied"

    def test_delete_product_success(self, product_1, seller_1, request_factory):
        assert Product.objects.count() == 1

        response = self.send_request(request_factory, None, seller_1, "delete", "destroy")
        assert response.status_code == 204

        assert Product.objects.count() == 0

    def test_seller_cannot_delete_product_of_another_seller(
        self, product_1, seller_2, request_factory
    ):
        assert Product.objects.count() == 1

        response = self.send_request(request_factory, None, seller_2, "delete", "destroy")
        assert response.status_code == 403

        assert Product.objects.count() == 1  # number of Products is still 1

    def test_buyer_cannot_create_product(self, buyer_1, request_factory):
        data = {"name": "test product", "cost": 100, "available_amount": 86}

        assert Product.objects.count() == 0

        response = self.send_request(request_factory, data, buyer_1, "post", "create")
        assert response.status_code == 403

        assert Product.objects.count() == 0
