from rest_framework import permissions

class IsClientOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow clients to create jobs.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to clients
        return request.user.is_authenticated and request.user.user_type == 'client'

class IsJobOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a job to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner of the job
        return obj.client == request.user
