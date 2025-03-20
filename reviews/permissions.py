from rest_framework import permissions

class IsReviewerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow reviewers to edit their own reviews.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the reviewer
        return obj.reviewer == request.user
