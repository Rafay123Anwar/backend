from rest_framework import permissions

class IsFreelancerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow freelancers to create proposals.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to freelancers
        return request.user.is_authenticated and request.user.user_type == 'freelancer'

class IsProposalOwnerOrJobOwner(permissions.BasePermission):
    """
    Custom permission to only allow proposal owners or job owners to view or modify a proposal.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is the proposal owner (freelancer) or the job owner (client)
        return (obj.freelancer == request.user) or (obj.job.client == request.user)
