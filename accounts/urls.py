from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)

from .views import SignUpAPIView


app_name = "accounts"

urlpatterns = [
    # obtain jwt token
    path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    # path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path("signup", SignUpAPIView.as_view(), name="signup"),
]
