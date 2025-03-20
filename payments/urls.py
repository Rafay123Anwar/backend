from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, BankAccountViewSet

router = DefaultRouter()
router.register(r'', PaymentViewSet, basename='payment')
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-account')

urlpatterns = [
    path('', include(router.urls)),
]
