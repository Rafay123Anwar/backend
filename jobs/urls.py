from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewSet, CategoryViewSet,CategoryListView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'', JobViewSet, basename='job')

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('', include(router.urls)),
]
