from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProposalViewSet, JobProposalsListView, MyProposalsListView

router = DefaultRouter()
router.register(r'', ProposalViewSet, basename='proposal')

urlpatterns = [
    path('job/<int:job_id>/', JobProposalsListView.as_view(), name='job-proposals'),
    path('my/', MyProposalsListView.as_view(), name='my-proposals'),
    path('', include(router.urls)),
]
