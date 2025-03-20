from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from .permissions import IsChatParticipant

class ChatRoomViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatParticipant]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chat_room = self.get_object()
        messages = chat_room.messages.all()
        
        # Mark messages as read
        messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsChatParticipant]
    
    def get_queryset(self):
        chat_room_id = self.kwargs.get('chat_room_id')
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        
        # Check if the user is a participant in the chat room
        if self.request.user not in chat_room.participants.all():
            return Message.objects.none()
        
        return chat_room.messages.all()
    
    def perform_create(self, serializer):
        chat_room_id = self.kwargs.get('chat_room_id')
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        
        # Check if the user is a participant in the chat room
        if self.request.user not in chat_room.participants.all():
            raise permissions.PermissionDenied("You are not a participant in this chat room.")
        
        serializer.save(sender=self.request.user, chat_room=chat_room)
        
        # Create a notification for other participants
        from notifications.models import Notification
        for participant in chat_room.participants.exclude(id=self.request.user.id):
            Notification.objects.create(
                recipient=participant,
                sender=self.request.user,
                notification_type='new_message',
                content=f'New message from {self.request.user.first_name} {self.request.user.last_name}',
                related_job=chat_room.job
            )
