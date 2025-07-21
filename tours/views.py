from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import PermissionDenied
from django.http import Http404
import logging

from .serializers import (
    UserSerializer, TripSerializer, LocationSerializer, 
    ExpenseSerializer, ExpenseSummarySerializer
)
from .models import Trip, Location, Expense, ExpenseSummary
from .permissions import IsVisitor, IsGuideOwnerOrReadOnly, IsAdmin


logger = logging.getLogger(__name__)
User = get_user_model()


class UserViewSet(viewsets.GenericViewSet):
    """User registration ViewSet"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """User registration endpoint"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TripViewSet(viewsets.ModelViewSet):
    """Trip CRUD operations ViewSet"""
    serializer_class = TripSerializer
    permission_classes = [IsGuideOwnerOrReadOnly | IsAdmin | IsVisitor]
    
    def get_queryset(self): #type: ignore
        user = self.request.user
        if user.role == 'admin':  #type: ignore
            return Trip.objects.all()
        return Trip.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can't DELETE this Trip")
        
        logger.info(f"User {self.request.user.pk} deleting trip: {instance.id}")
        print(f"Deleting trip: {instance}")
        instance.delete()
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"message": "Trip successfully deleted", "id": kwargs.get('pk')}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class LocationViewSet(viewsets.ModelViewSet):
    """Location CRUD operations ViewSet"""
    serializer_class = LocationSerializer
    permission_classes = [IsGuideOwnerOrReadOnly | IsAdmin]
    
    def get_queryset(self): #type: ignore
        user = self.request.user 
        if user.role == 'admin': #type: ignore
            return Location.objects.all()
        return Location.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can't DELETE this Location")
        
        logger.info(f"User {self.request.user.pk} deleting location: {instance.id}")
        print(f"Deleting location: {instance}")
        instance.delete()


class ExpenseViewSet(viewsets.ModelViewSet):
    """Expense CRUD operations ViewSet"""
    serializer_class = ExpenseSerializer
    permission_classes = [IsGuideOwnerOrReadOnly | IsAdmin]
    
    def get_queryset(self): #type: ignore
        user = self.request.user
        trip_id = self.kwargs.get('trip_id')
        
        if user.role == 'admin': #type: ignore
            if trip_id:
                return Expense.objects.filter(trip__id=trip_id)
            return Expense.objects.all()
        
        if trip_id:
            return Expense.objects.filter(trip__id=trip_id, trip__user=user)
        return Expense.objects.filter(trip__user=user)
    
    def perform_create(self, serializer):
        trip_id = self.kwargs.get('trip_id')
        if trip_id:
            try:
                trip = Trip.objects.get(id=trip_id, user=self.request.user)
                serializer.save(trip=trip)
            except Trip.DoesNotExist:
                raise Http404("Trip not found")
        else:
            serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
        if instance.trip.user != self.request.user:
            raise PermissionDenied("You can't DELETE this expense!")
        
        logger.info(f"User {self.request.user.pk} deleting expense: {instance.id}")
        print(f"Deleting expense: {instance}")
        instance.delete()
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"message": "Expense successfully deleted", "id": kwargs.get('pk')}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ExpenseSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """Expense Summary read-only ViewSet"""
    serializer_class = ExpenseSummarySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):    #type: ignore
        user = self.request.user
        return ExpenseSummary.objects.filter(trip__user=user)
    
    @action(detail=False, methods=['get'], url_path='by-trip/(?P<trip_id>[^/.]+)')
    def get_by_trip(self, request, trip_id=None):
        """Get expense summary by trip ID"""
        try:
            trip = Trip.objects.get(id=trip_id, user=request.user)
        except Trip.DoesNotExist:
            raise Http404("Trip not found or you do not have permission.")
        
        try:
            summary = ExpenseSummary.objects.get(trip=trip)
            serializer = self.get_serializer(summary)
            return Response(serializer.data)
        except ExpenseSummary.DoesNotExist:
            raise Http404("Expense summary not found for this trip.")


# urls.py-ისთვის
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'expense-summaries', ExpenseSummaryViewSet, basename='expense-summary')

# Trip-specific expenses-ისთვის nested routing გჭირდება
# რეკომენდაცია: drf-nested-routers package გამოიყენო

urlpatterns = router.urls










# from django.contrib.auth import get_user_model
# from rest_framework import generics
# from .serializers import UserSerializer, TripSerializer, LocationSerializer, ExpenseSerializer,ExpenseSummarySerializer
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from .models import Trip,Location,Expense,ExpenseSummary
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.exceptions import PermissionDenied
# import logging
# from django.http import Http404
# from .permissions import IsVisitor, IsGuideOwnerOrReadOnly, IsAdmin


# logger = logging.getLogger(__name__)
# User = get_user_model()

# class CreateUserView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AllowAny]

# class TripListCreate(generics.ListCreateAPIView):
#     serializer_class = TripSerializer
#     permission_classes = [IsGuideOwnerOrReadOnly | IsAdmin | IsVisitor]

#     def get_queryset(self): #type: ignore
#         return Trip.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

# class TripDestroyApiView(generics.RetrieveDestroyAPIView):
#     serializer_class = TripSerializer
#     permission_classes = [IsGuideOwnerOrReadOnly | IsAdmin]
#     lookup_field = 'pk'
    
#     def get_queryset(self): #type: ignore
#         user = self.request.user
#         if user.role == 'admin': # type: ignore
#             return Trip.objects.all()
#         return Trip.objects.filter(user=user)
    
#     def perform_destroy(self, instance):
#         if instance.user != self.request.user:
#             raise PermissionDenied("You can't DELETE this Trip")
        
#         logger.info(f"User {self.request.user.pk} deleting trip: {instance.id}")
#         print(f"Deleting trip: {instance}")
#         instance.delete()
    
#     def delete(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             return Response(
#                 {"message": "Trip successfully deleted", "id": kwargs.get('pk')}, 
#                 status=status.HTTP_204_NO_CONTENT
#             )
#         except Exception as e:
#             return Response(
#                 {"error": str(e)}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )


# class TripUpdateView(generics.RetrieveUpdateAPIView):
#     serializer_class = TripSerializer
#     permission_classes = [IsGuideOwnerOrReadOnly | IsAdmin]


#     def get_queryset(self): #type: ignore
#         return Trip.objects.filter(user=self.request.user)


#     def perform_update(self, serializer):
#         serializer.save(user=self.request.user)


# class LocationCreateApiView(generics.ListCreateAPIView):
#     serializer_class = LocationSerializer
#     permission_classes = [IsGuideOwnerOrReadOnly | IsAdmin]

#     def get_queryset(self): #type: ignore
#         return Location.objects.filter(user=self.request.user)
    
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# class LocationDestroyUpdateApiView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = LocationSerializer 
#     permission_classes = [IsGuideOwnerOrReadOnly | IsAdmin]
#     lookup_field = 'pk'

#     def get_queryset(self): #type: ignore
#         user = self.request.user
#         if user.role == 'admin': # type: ignore
#             return Location.objects.all()
#         return Location.objects.filter(user=user)


#     def perform_destroy(self, instance):
#         if instance.user != self.request.user:
#             raise PermissionDenied("You can't DELETE this Location")
        
#         logger.info(f"User {self.request.user.pk} deleting location: {instance.id}")
#         print(f"Deleting location: {instance}")
#         instance.delete()


# class ExpenseListCreateView(generics.ListCreateAPIView):
#     serializer_class = ExpenseSerializer
#     permission_classes = [IsGuideOwnerOrReadOnly | IsAdmin]

#     def get_queryset(self): #type: ignore
#         trip_id = self.kwargs['trip_id']
#         return Expense.objects.filter(trip__id=trip_id, trip__user=self.request.user)

#     def perform_create(self, serializer):
#         trip_id = self.kwargs['trip_id']
#         try:
#             trip = Trip.objects.get(id=trip_id, user=self.request.user)
#             serializer.save(trip=trip)
#         except Trip.DoesNotExist:
#             raise Http404("Trip not found")

# class ExnenseDeleteApiView(generics.RetrieveDestroyAPIView):
#     serializer_class = ExpenseSerializer
#     permission_classes = [IsGuideOwnerOrReadOnly | IsAdmin]
#     lookup_field = 'pk'

#     def get_queryset(self): #type: ignore
#         user = self.request.user
#         if user.role == 'admin': # type: ignore
#             return Location.objects.all()
#         return Location.objects.filter(user=user)

#     def perform_destroy(self, instance):
#         if instance.user != self.request.user:
#             raise PermissionDenied("You can't DELETE this expense !")
        
#         logger.info(f"user{self.request.user.pk} deleting expense: instance.id")
#         print(f"Deleting expense: {instance}")
#         instance.delete()
    
#     def delete(self,request,*args, **kwargs):
#         try:
#             instance = self.get_object()
#             self.perform_destroy(instance)
#             return Response(
#                 {"message": "Expense successfully deleted", "id": kwargs.get('pk')}, 
#                 status=status.HTTP_204_NO_CONTENT
#             )
#         except Exception as e:
#             return Response(
#                 {"error": str(e)}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )


# class ExpenseUpdateApiView(generics.RetrieveUpdateAPIView):
#     serializer_class = ExpenseSerializer
#     permission_classes = [IsGuideOwnerOrReadOnly | IsAdmin]

#     def get_queryset(self): #type: ignore
#         user = self.request.user
#         if user.role == 'admin': # type: ignore
#             return Expense.objects.all()
#         return Expense.objects.filter(user=user)
    
#     def perform_update(self,serializer):
#         serializer.save(user=self.request.user)


# class ExpenseSummaryDetailView(generics.RetrieveAPIView):
#     serializer_class = ExpenseSummarySerializer
#     permission_classes = [IsAuthenticated]

# def get_object(self) -> ExpenseSummary:
#     trip_id = self.kwargs.get(self.lookup_url_kwarg)
#     try:
#         trip = Trip.objects.get(id=trip_id, user=self.request.user)
#     except Trip.DoesNotExist:
#         raise Http404("Trip not found or you do not have permission.")
    
#     try:
#         summary = ExpenseSummary.objects.get(trip=trip)
#     except ExpenseSummary.DoesNotExist:
#         raise Http404("Expense summary not found for this trip.")
#     return summary



