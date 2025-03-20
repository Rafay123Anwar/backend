from rest_framework import permissions

class IsChatParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a chat room to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in the chat room
        return request.user in obj.participants.all()
