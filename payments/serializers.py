from rest_framework import serializers
from .models import Payment, BankAccount
from accounts.serializers import UserSerializer
from jobs.serializers import JobSerializer

class PaymentSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(source='sender', read_only=True)
    recipient_details = UserSerializer(source='recipient', read_only=True)
    job_details = JobSerializer(source='job', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'sender', 'sender_details', 'recipient', 'recipient_details',
            'job', 'job_details', 'amount', 'payment_type', 'status',
            'stripe_payment_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['sender', 'status', 'stripe_payment_id', 'created_at', 'updated_at']

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'id', 'user', 'account_holder_name', 'account_number',
            'routing_number', 'bank_name', 'is_default', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
