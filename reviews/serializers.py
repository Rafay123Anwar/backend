from rest_framework import serializers
from .models import Review
from accounts.serializers import UserSerializer
from jobs.serializers import JobSerializer

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_details = UserSerializer(source='reviewer', read_only=True)
    recipient_details = UserSerializer(source='recipient', read_only=True)
    job_details = JobSerializer(source='job', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'job', 'job_details', 'reviewer', 'reviewer_details',
            'recipient', 'recipient_details', 'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['reviewer', 'created_at']
    
    def validate(self, attrs):
        job = attrs.get('job')
        recipient = attrs.get('recipient')
        reviewer = self.context['request'].user
        
        # Check if the job is completed
        if job.status != 'completed':
            raise serializers.ValidationError({"job": "You can only review completed jobs."})
        
        # Check if the reviewer is either the client or the freelancer of the job
        if reviewer != job.client and not job.proposals.filter(freelancer=reviewer, status='accepted').exists():
            raise serializers.ValidationError({"reviewer": "You must be involved in the job to leave a review."})
        
        # Check if the recipient is either the client or the freelancer of the job
        if recipient != job.client and not job.proposals.filter(freelancer=recipient, status='accepted').exists():
            raise serializers.ValidationError({"recipient": "The recipient must be involved in the job."})
        
        # Check if the reviewer and recipient are different users
        if reviewer == recipient:
            raise serializers.ValidationError({"recipient": "You cannot review yourself."})
        
        # Check if the reviewer has already reviewed this recipient for this job
        if Review.objects.filter(job=job, reviewer=reviewer, recipient=recipient).exists():
            raise serializers.ValidationError({"job": "You have already reviewed this user for this job."})
        
        return attrs
    
    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)
