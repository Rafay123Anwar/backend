from rest_framework import serializers
from .models import ChatRoom, Message
from accounts.serializers import UserSerializer
from jobs.serializers import JobSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(source='sender', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'chat_room', 'sender', 'sender_details', 'content', 'is_read', 'created_at']
        read_only_fields = ['sender', 'is_read', 'created_at']

class ChatRoomSerializer(serializers.ModelSerializer):
    job_details = JobSerializer(source='job', read_only=True)
    participants_details = UserSerializer(source='participants', many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'job', 'job_details', 'participants', 'participants_details', 
                  'last_message', 'unread_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return {
                'id': last_message.id,
                'content': last_message.content,
                'sender': last_message.sender.id,
                'created_at': last_message.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()
