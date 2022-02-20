from django.urls import include, path
from rest_framework import routers
from vending import views

router = routers.DefaultRouter()
router.register("product", views.ProductViewSet)
router.register("user", views.UserViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
