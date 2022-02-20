import json

import pytest
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from vending.models import User
from vending.views import ProductViewSet


@pytest.mark.django_db
class TestBuy:
    def send_request(self, rf: APIRequestFactory, data: str, user: User) -> Response:
        endpoint = f"/vending-machine/product/buy/"
        request = rf.post(endpoint, data=data, content_type="application/json")
        force_authenticate(request, user=user)
        view = ProductViewSet.as_view({"post": "buy"})
        response = view(request)

        return response

    def test_buy_success(self, buyer_1, product_1, request_factory):
        data = json.dumps({"product_id": product_1.pk, "amount": 2})

        buyer_1.deposit = 100
        buyer_1.save()

        response = self.send_request(request_factory, data, buyer_1)
        assert response.status_code == 200

        assert buyer_1.deposit == 90
        product_1.refresh_from_db()
        assert product_1.available_amount == 58

        change = response.data["change"]
        assert change == [50, 20, 20]

    def test_buy_insufficient_stock(self, buyer_2, product_2, request_factory):
        data = json.dumps({"product_id": product_2.pk, "amount": 200})

        buyer_2.deposit = 100
        buyer_2.save()

        response = self.send_request(request_factory, data, buyer_2)
        assert response.status_code == 404

        error = response.data["amount"]
        assert (
            error.title().lower()
            == "Not enough stock. You want to buy 200 Kinder Bueno but there is only 10 available.".lower()
        )
        assert buyer_2.deposit == 100  # deposit does not change

        product_2.refresh_from_db()
        assert product_2.available_amount == 10  # product stock does not change

    def test_buy_out_of_stock(self, buyer_2, product_2, request_factory):
        data = json.dumps({"product_id": product_2.pk, "amount": 200})

        product_2.available_amount = 0
        product_2.save()

        buyer_2.deposit = 100
        buyer_2.save()

        response = self.send_request(request_factory, data, buyer_2)
        assert response.status_code == 404

        error = response.data["product"]
        assert error.title().lower() == "Product Kinder Bueno is out of stock.".lower()
        assert buyer_2.deposit == 100  # deposit does not change

    def test_buy_insufficient_funds(self, buyer_2, product_2, request_factory):
        data = json.dumps({"product_id": product_2.pk, "amount": 5})

        buyer_2.deposit = 5
        buyer_2.save()

        response = self.send_request(request_factory, data, buyer_2)
        assert response.status_code == 406

        error = response.data["buyer"]
        assert error.title() is not None
        assert buyer_2.deposit == 5  # deposit does not change

        product_2.refresh_from_db()
        assert product_2.available_amount == 10  # product stock does not change

    def test_buy_seller_cannot_buy(self, seller_1, product_1, request_factory):
        data = json.dumps({"product_id": product_1.pk, "amount": 2})

        response = self.send_request(request_factory, data, seller_1)
        assert response.status_code == 403

        error = response.data["detail"]
        assert error.title() is not None
        assert error.code == "permission_denied"
