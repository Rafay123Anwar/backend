from rest_framework import serializers
from .models import Proposal
from jobs.serializers import JobSerializer
from accounts.serializers import UserSerializer, FreelancerProfileSerializer

class ProposalSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source='job', read_only=True)
    freelancer_details = UserSerializer(source='freelancer', read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'id', 'job', 'job_details', 'freelancer', 'freelancer_details',
            'cover_letter', 'bid_amount', 'estimated_time', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['freelancer', 'status', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        # Check if the job is still open
        job = attrs.get('job')
        if job.status != 'open':
            raise serializers.ValidationError({"job": "This job is no longer accepting proposals."})
        
        # Check if the user is a freelancer
        user = self.context['request'].user
        if user.user_type != 'freelancer':
            raise serializers.ValidationError({"freelancer": "Only freelancers can submit proposals."})
        
        # Check if the freelancer has already submitted a proposal for this job
        if Proposal.objects.filter(job=job, freelancer=user).exists():
            raise serializers.ValidationError({"job": "You have already submitted a proposal for this job."})
        
        return attrs
    
    def create(self, validated_data):
        validated_data['freelancer'] = self.context['request'].user
        return super().create(validated_data)

class ProposalDetailSerializer(ProposalSerializer):
    freelancer_profile = serializers.SerializerMethodField()
    
    class Meta(ProposalSerializer.Meta):
        fields = ProposalSerializer.Meta.fields + ['freelancer_profile']
    
    def get_freelancer_profile(self, obj):
        from accounts.models import FreelancerProfile
        profile = FreelancerProfile.objects.get(user=obj.freelancer)
        return FreelancerProfileSerializer(profile).data
