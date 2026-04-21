from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserRegistrationApi, GoogleLoginApi, LoginApi

urlpatterns = [
    # Custom login: accepts username or email
    path('login/', LoginApi.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Registration
    path('register/', UserRegistrationApi.as_view(), name='register'),

    # Google OAuth
    path('google-login/', GoogleLoginApi.as_view(), name='google_login'),
]
