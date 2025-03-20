from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import FreelancerProfile, ClientProfile, Portfolio
from django.db import models

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'user_type', 'is_email_verified']
        read_only_fields = ['is_email_verified']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'user_type']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if attrs['user_type'] not in ['freelancer', 'client']:
            raise serializers.ValidationError({"user_type": "User type must be either 'freelancer' or 'client'."})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        
        # Create corresponding profile
        if user.user_type == 'freelancer':
            FreelancerProfile.objects.create(user=user)
        elif user.user_type == 'client':
            ClientProfile.objects.create(user=user)
            
        return user

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['id', 'title', 'description', 'image', 'url', 'created_at']

class FreelancerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    portfolio_items = PortfolioSerializer(many=True, read_only=True)
    total_jobs_applied = serializers.SerializerMethodField()
    total_proposals_sent = serializers.SerializerMethodField()
    total_earnings = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = FreelancerProfile
        fields = [
            'id', 'user', 'profile_picture', 'bio', 'skills', 'experience_years', 
            'hourly_rate', 'wallet_balance', 'portfolio_items', 'total_jobs_applied',
            'total_proposals_sent', 'total_earnings', 'average_rating'
        ]
        read_only_fields = ['wallet_balance', 'user']
    
    def get_total_jobs_applied(self, obj):
        return obj.user.proposals.count()
    
    def get_total_proposals_sent(self, obj):
        return obj.user.proposals.count()
    
    def get_total_earnings(self, obj):
        from payments.models import Payment
        return Payment.objects.filter(recipient=obj.user, status='completed').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
    
    def get_average_rating(self, obj):
        from reviews.models import Review
        reviews = Review.objects.filter(recipient=obj.user)
        if reviews.exists():
            return reviews.aggregate(avg=models.Avg('rating'))['avg']
        return 0

class ClientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    total_jobs_posted = serializers.SerializerMethodField()
    total_proposals_received = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientProfile
        fields = [
            'id', 'user', 'profile_picture', 'company_name', 
            'wallet_balance', 'total_jobs_posted', 'total_proposals_received'
        ]
        read_only_fields = ['wallet_balance', 'user']
    
    def get_total_jobs_posted(self, obj):
        return obj.user.jobs.count()
    
    def get_total_proposals_received(self, obj):
        from proposals.models import Proposal
        from jobs.models import Job
        job_ids = Job.objects.filter(client=obj.user).values_list('id', flat=True)
        return Proposal.objects.filter(job_id__in=job_ids).count()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, validators=[validate_password])

class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
