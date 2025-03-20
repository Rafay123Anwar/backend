from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')

urlpatterns = [
    path('rooms/<int:chat_room_id>/messages/', MessageViewSet.as_view({'get': 'list', 'post': 'create'}), name='room-messages'),
    path('', include(router.urls)),
]
