from rest_framework import serializers
from .models import Notification
from accounts.serializers import UserSerializer
from jobs.serializers import JobSerializer

class NotificationSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(source='sender', read_only=True)
    job_details = JobSerializer(source='related_job', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'sender_details', 'notification_type',
            'content', 'is_read', 'related_job', 'job_details', 'created_at'
        ]
        read_only_fields = ['recipient', 'sender', 'notification_type', 'content', 'related_job', 'created_at']
