import uuid
from django.contrib.auth import get_user_model
# from django.core.mail import send_mail
from django.conf import settings
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import FreelancerProfile, ClientProfile, Portfolio, EmailVerification, PasswordReset
from django.db import models
from .serializers import (
    UserSerializer, RegisterSerializer, FreelancerProfileSerializer, 
    ClientProfileSerializer, PortfolioSerializer, ChangePasswordSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    EmailVerificationSerializer
)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate verification token and send email
        token = str(uuid.uuid4())
        EmailVerification.objects.create(user=user, token=token)
        
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
        # send_mail(
        #     'Verify your email',
        #     f'Please click the link to verify your email: {verification_url}',
        #     settings.DEFAULT_FROM_EMAIL,
        #     [user.email],
        #     fail_silently=False,
        # )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
            'message': 'User registered successfully. Please verify your email.'
        }, status=status.HTTP_201_CREATED)

# class EmailVerificationView(APIView):
#     permission_classes = [permissions.AllowAny]
    
#     def post(self, request):
#         serializer = EmailVerificationSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         token = serializer.validated_data['token']
#         try:
#             verification = EmailVerification.objects.get(token=token)
#             user = verification.user
#             user.is_email_verified = True
#             user.save()
#             verification.delete()
            
#             return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
#         except EmailVerification.DoesNotExist:
#             return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            email = request.data.get('email')
            user = User.objects.get(email=email)
            response.data['user'] = UserSerializer(user).data
            
            # Determine redirect URL based on user type
            if user.user_type == 'freelancer':
                response.data['redirect'] = '/freelancer/dashboard'
            elif user.user_type == 'client':
                response.data['redirect'] = '/client/dashboard'
        
        return response

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token = str(uuid.uuid4())
            PasswordReset.objects.create(user=user, token=token)
            
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
            # send_mail(
            #     'Reset your password',
            #     f'Please click the link to reset your password: {reset_url}',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [email],
            #     fail_silently=False,
            # )
            
            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # For security reasons, don't reveal that the email doesn't exist
            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']
        
        try:
            reset = PasswordReset.objects.get(token=token)
            user = reset.user
            user.set_password(password)
            user.save()
            reset.delete()
            
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        except PasswordReset.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class FreelancerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = FreelancerProfileSerializer
    
    def get_object(self):
        return FreelancerProfile.objects.get(user=self.request.user)

class ClientProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    
    def get_object(self):
        return ClientProfile.objects.get(user=self.request.user)

class PortfolioListCreateView(generics.ListCreateAPIView):
    serializer_class = PortfolioSerializer
    
    def get_queryset(self):
        return Portfolio.objects.filter(freelancer__user=self.request.user)
    
    def perform_create(self, serializer):
        freelancer = FreelancerProfile.objects.get(user=self.request.user)
        serializer.save(freelancer=freelancer)

class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PortfolioSerializer
    
    def get_queryset(self):
        return Portfolio.objects.filter(freelancer__user=self.request.user)

class FreelancerStatsView(APIView):
    def get(self, request):
        try:
            freelancer = FreelancerProfile.objects.get(user=request.user)
            
            from proposals.models import Proposal
            from payments.models import Payment
            from reviews.models import Review
            
            total_jobs_applied = Proposal.objects.filter(freelancer=request.user).count()
            total_proposals_sent = Proposal.objects.filter(freelancer=request.user).count()
            total_earnings = Payment.objects.filter(recipient=request.user, status='completed').aggregate(
                total=models.Sum('amount')
            )['total'] or 0
            total_reviews = Review.objects.filter(recipient=request.user).count()
            
            return Response({
                'total_jobs_applied': total_jobs_applied,
                'total_proposals_sent': total_proposals_sent,
                'total_earnings': total_earnings,
                'total_reviews': total_reviews,
                'wallet_balance': freelancer.wallet_balance
            }, status=status.HTTP_200_OK)
        except FreelancerProfile.DoesNotExist:
            return Response({'error': 'Freelancer profile not found'}, status=status.HTTP_404_NOT_FOUND)

class ClientStatsView(APIView):
    def get(self, request):
        try:
            client = ClientProfile.objects.get(user=request.user)
            
            from jobs.models import Job
            from proposals.models import Proposal
            from reviews.models import Review
            
            total_jobs_posted = Job.objects.filter(client=request.user).count()
            job_ids = Job.objects.filter(client=request.user).values_list('id', flat=True)
            total_proposals_received = Proposal.objects.filter(job_id__in=job_ids).count()
            total_reviews_given = Review.objects.filter(reviewer=request.user).count()
            
            return Response({
                'total_jobs_posted': total_jobs_posted,
                'total_proposals_received': total_proposals_received,
                'total_reviews_given': total_reviews_given,
                'wallet_balance': client.wallet_balance
            }, status=status.HTTP_200_OK)
        except ClientProfile.DoesNotExist:
            return Response({'error': 'Client profile not found'}, status=status.HTTP_404_NOT_FOUND)
