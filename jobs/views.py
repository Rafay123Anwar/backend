from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job, Category
from .serializers import JobSerializer, CategorySerializer
from .permissions import IsClientOrReadOnly, IsJobOwner

##addition
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for categories
##addition
    
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'job_type', 'status']
    search_fields = ['title', 'description', 'skills_required']
    ordering_fields = ['created_at', 'budget']
    
    def get_queryset(self):
        # queryset = Job.objects.all()
        queryset = Job.objects.all().order_by('-created_at') 
        
        # Filter by budget range
        min_budget = self.request.query_params.get('min_budget')
        max_budget = self.request.query_params.get('max_budget')
        
        if min_budget:
            queryset = queryset.filter(budget__gte=min_budget)
        if max_budget:
            queryset = queryset.filter(budget__lte=max_budget)
            
        # Filter by skills
        skills = self.request.query_params.get('skills')
        if skills:
            skills_list = skills.split(',')
            for skill in skills_list:
                queryset = queryset.filter(skills_required__contains=[skill])
        
        return queryset
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsJobOwner]
        elif self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    def mark_in_progress(self, request, pk=None):
        job = self.get_object()
        if job.client != request.user:
            return Response({'error': 'You do not have permission to perform this action.'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        job.status = 'in_progress'
        job.save()
        return Response({'status': 'job marked as in progress'})
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        job = self.get_object()
        if job.client != request.user:
            return Response({'error': 'You do not have permission to perform this action.'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        job.status = 'completed'
        job.save()
        return Response({'status': 'job marked as completed'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        job = self.get_object()
        if job.client != request.user:
            return Response({'error': 'You do not have permission to perform this action.'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        job.status = 'cancelled'
        job.save()
        return Response({'status': 'job cancelled'})
