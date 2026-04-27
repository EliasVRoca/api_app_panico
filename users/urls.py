from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, MeView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('users/me', MeView.as_view(), name='user-me'),
    path('', include(router.urls)),
]
