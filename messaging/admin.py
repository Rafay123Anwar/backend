from django.contrib import admin
from .models import ChatRoom, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0

class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'created_at')
    search_fields = ('job__title',)
    inlines = [MessageInline]

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chat_room', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('content', 'sender__email')
    date_hierarchy = 'created_at'

admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(Message, MessageAdmin)
