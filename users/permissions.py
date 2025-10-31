# from rest_framework import permissions

# class IsAdminOrReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return (
#             request.method in permissions.SAFE_METHODS 
#             or (request.user and request.user.is_staff)
#         )

# class IsDonor(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return hasattr(request.user, 'role') and request.user.role == 'donor'

# class IsReceiver(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return hasattr(request.user, 'role') and request.user.role == 'receiver'


from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow only admins to edit; others read-only."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user and request.user.is_staff
        )

class IsDonorOrReceiver(permissions.BasePermission):
    """Allow access only to donor/receiver/exchanger."""
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role in [
            'donor', 'receiver', 'exchanger'
        ]

class IsSelfOrAdmin(permissions.BasePermission):
    """User can access own profile; admin can access all."""
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff
