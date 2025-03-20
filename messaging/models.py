from django.db import models
from django.contrib.auth import get_user_model
from jobs.models import Job

User = get_user_model()

class ChatRoom(models.Model):
    """Model for chat rooms between clients and freelancers."""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='chat_rooms')
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat for {self.job.title}"

class Message(models.Model):
    """Model for messages in a chat room."""
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.email} at {self.created_at}"
