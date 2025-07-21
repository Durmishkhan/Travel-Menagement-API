from rest_framework import permissions

class IsVisitor(permissions.BasePermission):
    def has_permission(self, request, view): # type: ignore
        return (
            request.user.is_authenticated and 
            request.user.role == 'visitor' and 
            request.method in permissions.SAFE_METHODS
        )


class IsGuideOwnerOrReadOnly(permissions.BasePermission):
   def has_object_permission(self, request, view, obj): # type: ignore
        if not request.user.is_authenticated:
            return False

        if request.user.role == 'admin':
            return True

        if request.user.role == 'guide':
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.user == request.user 

        return request.method in permissions.SAFE_METHODS


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.role == 'admin'
