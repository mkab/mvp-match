import json

import pytest
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from vending.models import User
from vending.views import UserViewSet


@pytest.mark.django_db
class TestDeposit:
    def send_request(
        self,
        rf: APIRequestFactory,
        data: str,
        user_1: User,
        user_2: User,
    ) -> Response:
        endpoint = f"/vending-machine/user/{user_1.pk}/deposit/"
        request = rf.post(endpoint, data=data, content_type="application/json")
        force_authenticate(request, user=user_2)
        view = UserViewSet.as_view({"post": "deposit"})
        response = view(request, pk=user_1.pk)

        return response

    def test_deposit_success(self, buyer_1, request_factory):
        data = json.dumps({"deposit": 5})

        assert buyer_1.deposit == 0

        response = self.send_request(request_factory, data, buyer_1, buyer_1)
        assert response.status_code == 200

        buyer_1.refresh_from_db()
        assert buyer_1.deposit == 5

        # deposit another 5 cents
        response = self.send_request(request_factory, data, buyer_1, buyer_1)
        buyer_1.refresh_from_db()
        assert buyer_1.deposit == 10  # deposit should be 10

    def test_deposit_failure_unaccepted_coins(self, buyer_1, request_factory):
        data = json.dumps({"deposit": 11})

        assert buyer_1.deposit == 0
        response = self.send_request(request_factory, data, buyer_1, buyer_1)

        assert response.status_code == 400

        error = response.data["detail"]
        assert error.title() is not None

        buyer_1.refresh_from_db()
        assert buyer_1.deposit == 0

    def test_deposit_failure_permission_denied(self, buyer_1, buyer_2, request_factory):
        data = json.dumps({"deposit": 50})

        assert buyer_1.deposit == 0
        response = self.send_request(request_factory, data, buyer_1, buyer_2)
        assert response.status_code == 403

        error = response.data["detail"]
        assert error.title() is not None
        assert error.code == "permission_denied"

        buyer_1.refresh_from_db()
        assert buyer_1.deposit == 0

    def test_deposit_failure_seller(self, seller_1, request_factory):
        data = json.dumps({"deposit": 50})

        assert seller_1.deposit == 0
        response = self.send_request(request_factory, data, seller_1, seller_1)
        assert response.status_code == 403

        error = response.data["detail"]
        assert error.title() is not None
        assert error.code == "permission_denied"

        seller_1.refresh_from_db()
        assert seller_1.deposit == 0
