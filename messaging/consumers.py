import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Check if the user is authenticated
        if not self.scope['user'].is_authenticated:
            await self.close()
            return
        
        # Check if the user is a participant in the chat room
        is_participant = await self.is_chat_participant(self.scope['user'].id, self.room_id)
        if not is_participant:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        # Save message to database
        message_obj = await self.save_message(
            self.scope['user'].id,
            self.room_id,
            message
        )
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': self.scope['user'].id,
                'sender_name': f"{self.scope['user'].first_name} {self.scope['user'].last_name}",
                'message_id': message_obj['id'],
                'timestamp': message_obj['created_at'].isoformat()
            }
        )
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def is_chat_participant(self, user_id, room_id):
        try:
            user = User.objects.get(id=user_id)
            chat_room = ChatRoom.objects.get(id=room_id)
            return chat_room.participants.filter(id=user.id).exists()
        except (User.DoesNotExist, ChatRoom.DoesNotExist):
            return False
    
    @database_sync_to_async
    def save_message(self, user_id, room_id, content):
        user = User.objects.get(id=user_id)
        chat_room = ChatRoom.objects.get(id=room_id)
        message = Message.objects.create(
            sender=user,
            chat_room=chat_room,
            content=content
        )
        return {
            'id': message.id,
            'created_at': message.created_at
        }
