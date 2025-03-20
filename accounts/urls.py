from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, CustomTokenObtainPairView, ChangePasswordView,
    PasswordResetRequestView, PasswordResetConfirmView,
    # PasswordResetRequestView, PasswordResetConfirmView, EmailVerificationView,
    FreelancerProfileView, ClientProfileView, PortfolioListCreateView,
    PortfolioDetailView, FreelancerStatsView, ClientStatsView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('verify-email/', EmailVerificationView.as_view(), name='verify_email'),
    
    # Profiles
    path('freelancer/profile/', FreelancerProfileView.as_view(), name='freelancer_profile'),
    path('client/profile/', ClientProfileView.as_view(), name='client_profile'),
    
    # Portfolio
    path('portfolio/', PortfolioListCreateView.as_view(), name='portfolio_list'),
    path('portfolio/<int:pk>/', PortfolioDetailView.as_view(), name='portfolio_detail'),
    
    # Stats
    path('freelancer/stats/', FreelancerStatsView.as_view(), name='freelancer_stats'),
    path('client/stats/', ClientStatsView.as_view(), name='client_stats'),
]
