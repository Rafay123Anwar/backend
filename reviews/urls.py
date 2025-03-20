from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, JobReviewsListView, UserReviewsListView

router = DefaultRouter()
router.register(r'', ReviewViewSet, basename='review')

urlpatterns = [
    path('job/<int:job_id>/', JobReviewsListView.as_view(), name='job-reviews'),
    path('user/<int:user_id>/', UserReviewsListView.as_view(), name='user-reviews'),
    path('', include(router.urls)),
]
