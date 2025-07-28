from rest_framework import  permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

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



class TripPermission(BasePermission):
    def has_permission(self, request, view): #type: ignore
        user = request.user

        if not user.is_authenticated:
            return False
        
        if user.role == 'admin':
            return True
        
        if user.role == 'guide':
            return True
        
        if user.role == 'visitor':
            return request.method in SAFE_METHODS
    
        return False
    
from rest_framework.permissions import BasePermission, SAFE_METHODS

class LocationPermission(BasePermission):
    def has_permission(self, request, view): #type: ignore
        user = request.user

        if not user.is_authenticated:
            return False
        if user.role in ['admin', 'guide']:
            return True
        if user.role == 'visitor':
            return request.method in SAFE_METHODS
        return False

    def has_object_permission(self, request, view, obj): #type: ignore
        user = request.user

        if user.role == 'admin':
            return True
        if user.role == 'guide':
            return request.method in SAFE_METHODS or obj.user == user
        if user.role == 'visitor':
            return request.method in SAFE_METHODS
        return False

class ExpensePermission(BasePermission):
    def has_permission(self, request, view): #type: ignore
        user = request.user
        if not user.is_authenticated:
            return False
        if user.role in ['admin', 'guide']:
            return True
        if user.role == 'visitor':
            return False
        return False  
    def has_object_permission(self, request, view, obj): #type: ignore
        user = request.user

        if user.role == 'admin':
            return True
        if user.role == 'guide':
            return request.method in SAFE_METHODS or obj.user == user
        if user.role == 'visitor':
            return False
        return False
