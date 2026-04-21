from django.urls import path
from .views import PanicEventActivateAPIView, PanicEventHistoryAPIView

urlpatterns = [
    path('activate/', PanicEventActivateAPIView.as_view(), name='panic-activate'),
    path('history/', PanicEventHistoryAPIView.as_view(), name='panic-history'),
]
