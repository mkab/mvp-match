from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from vending.choices import AcceptedCoins
from vending.models import Product, User
from vending.permissions import IsBuyer, IsSeller, ProductAlterPermission, UserIsSelf
from vending.serializers import (
    DepositSerializer,
    ProductBuySerializer,
    ProductSerializer,
    UserSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        seller = request.user
        data = request.data
        data["seller_id"] = seller.id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"detail": "Product added successfully"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        seller = request.user
        data = request.data
        data["seller_id"] = seller.id

        return super().update(request, *args, **kwargs)

    @action(
        methods=["POST"],
        detail=False,
        url_path="buy",
        url_name="buyer-buys-product",
    )
    def buy(self, request, *args, **kwargs):
        serializer = ProductBuySerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        # data has been modified to include the other product information
        data = serializer.validated_data

        product: Product = data["product"]
        total_cost = data["total_cost"]
        buyer: User = request.user

        change_list = []
        temp_data = []

        change = buyer.deposit - total_cost
        buyer.deposit = change

        coins = sorted(AcceptedCoins.values, reverse=True)

        for coin in coins:
            count, change = divmod(change, coin)
            if count:
                temp_data.append({"count": count, "coin": coin})

        for temp in temp_data:
            change_list.extend([temp["coin"]] * temp["count"])

        # update product quantity
        product.available_amount -= data["amount"]
        product.save(update_fields=["available_amount"])

        # update buyer deposit
        buyer.save(update_fields=["deposit"])

        return Response(
            data={
                "total_spent": total_cost,
                "product": product.name,
                "change": change_list,
            },
        )

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []

        permission_classes = [IsAuthenticated]

        if self.action == "buy":
            permission_classes.append(IsBuyer)
        else:
            permission_classes.extend([IsSeller, ProductAlterPermission])
        return [permission() for permission in permission_classes]


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data={"detail": "User created successfully"}, status=status.HTTP_201_CREATED
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="deposit",
        url_name="buyer-deposit",
    )
    def deposit(self, request, pk):
        user = self.get_object()
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.deposit += serializer.validated_data["deposit"]
        user.save(update_fields=["deposit"])

        return Response(
            data={
                "id": user.id,
                "username": user.username,
                "deposit": user.deposit,
            },
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="reset",
        url_name="buyer-reset-deposit",
    )
    def reset(self, request, pk):
        user: User = self.get_object()
        user.deposit = 0
        user.save(update_fields=["deposit"])

        return Response(
            data={
                "id": user.id,
                "username": user.username,
                "deposit": user.deposit,
            },
        )

    def get_permissions(self):
        permission_classes = [
            IsAuthenticated,
        ]

        if self.action == "create":
            # POST requests should not require authentication
            return []
        elif self.action == "list":
            # only admins should be able to list all users
            permission_classes.append(IsAdminUser)
        elif self.action == "retrieve":
            # users can only retrieve their own
            permission_classes.append(UserIsSelf)
        else:
            permission_classes.extend([IsBuyer, UserIsSelf])

        return [permission() for permission in permission_classes]


# def login(request):
#     data = json.loads(request.body)
#     username = data.get("username")
#     password = data.get("password")

#     if username is None and password is None:
#         return JsonResponse("Please enter both username and password", status=400)

#     user = authenticate(username=username, password=password)
#     if user:
#         login(request, user)
#         return JsonResponse({"message": "Logged in!"})

#     return JsonResponse(
#         {"detail": "Invalid credentials"},
#         status=400,
#     )
