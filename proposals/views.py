from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Proposal
from jobs.models import Job
from .serializers import ProposalSerializer, ProposalDetailSerializer
from .permissions import IsFreelancerOrReadOnly, IsProposalOwnerOrJobOwner
from messaging.models import ChatRoom

class ProposalViewSet(viewsets.ModelViewSet):
    serializer_class = ProposalSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Filter by job if job_id is provided in the URL
        job_id = self.kwargs.get('job_id')
        if job_id:
            job = get_object_or_404(Job, id=job_id)
            
            # If the user is the job owner (client), return all proposals for the job
            if job.client == user:
                return Proposal.objects.filter(job=job)
            
            # If the user is a freelancer, only return their proposal for this job
            if user.user_type == 'freelancer':
                return Proposal.objects.filter(job=job, freelancer=user)
            
            return Proposal.objects.none()
        
        # If no job_id, return based on user type
        if user.user_type == 'freelancer':
            return Proposal.objects.filter(freelancer=user)
        elif user.user_type == 'client':
            return Proposal.objects.filter(job__client=user)
        
        return Proposal.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProposalDetailSerializer
        return ProposalSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [permissions.IsAuthenticated, IsFreelancerOrReadOnly]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsProposalOwnerOrJobOwner]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        proposal = self.get_object()
        
        # Check if the user is the job owner
        if proposal.job.client != request.user:
            return Response({'error': 'Only the job owner can accept proposals.'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        # Check if the job is still open
        if proposal.job.status != 'open':
            return Response({'error': 'This job is no longer accepting proposals.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Update proposal status
        proposal.status = 'accepted'
        proposal.save()
        
        # Update job status
        job = proposal.job
        job.status = 'in_progress'
        job.save()
        
        # Create a chat room for the client and freelancer
        chat_room = ChatRoom.objects.create(job=job)
        chat_room.participants.add(job.client, proposal.freelancer)
        
        # Reject all other proposals for this job
        Proposal.objects.filter(job=job).exclude(id=proposal.id).update(status='rejected')
        
        # Create notification for the freelancer
        from notifications.models import Notification
        Notification.objects.create(
            recipient=proposal.freelancer,
            sender=request.user,
            notification_type='proposal_accepted',
            content=f'Your proposal for "{job.title}" has been accepted!',
            related_job=job
        )
        
        return Response({'status': 'proposal accepted', 'chat_room_id': chat_room.id})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        proposal = self.get_object()
        
        # Check if the user is the job owner
        if proposal.job.client != request.user:
            return Response({'error': 'Only the job owner can reject proposals.'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        # Update proposal status
        proposal.status = 'rejected'
        proposal.save()
        
        # Create notification for the freelancer
        from notifications.models import Notification
        Notification.objects.create(
            recipient=proposal.freelancer,
            sender=request.user,
            notification_type='proposal_rejected',
            content=f'Your proposal for "{proposal.job.title}" has been rejected.',
            related_job=proposal.job
        )
        
        return Response({'status': 'proposal rejected'})
    
    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        proposal = self.get_object()
        
        # Check if the user is the proposal owner
        if proposal.freelancer != request.user:
            return Response({'error': 'Only the proposal owner can withdraw proposals.'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        # Check if the proposal is still pending
        if proposal.status != 'pending':
            return Response({'error': 'You can only withdraw pending proposals.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Update proposal status
        proposal.status = 'withdrawn'
        proposal.save()
        
        return Response({'status': 'proposal withdrawn'})

class JobProposalsListView(generics.ListCreateAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(Job, id=job_id)
        user = self.request.user
        
        # If the user is the job owner (client), return all proposals for the job
        if job.client == user:
            return Proposal.objects.filter(job=job)
        
        # If the user is a freelancer, only return their proposal for this job
        if user.user_type == 'freelancer':
            return Proposal.objects.filter(job=job, freelancer=user)
        
        return Proposal.objects.none()
    
    def perform_create(self, serializer):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(Job, id=job_id)
        serializer.save(freelancer=self.request.user, job=job)

class MyProposalsListView(generics.ListAPIView):
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'freelancer':
            return Proposal.objects.filter(freelancer=user)
        elif user.user_type == 'client':
            return Proposal.objects.filter(job__client=user)
        
        return Proposal.objects.none()
