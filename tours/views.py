from django.contrib.auth import get_user_model
from rest_framework import generics
from .serializers import UserSerializer, TripSerializer, LocationSerializer, ExpenseSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Trip,Location,Expense
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
import logging
from django.http import Http404


logger = logging.getLogger(__name__)
User = get_user_model()

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class TripListCreate(generics.ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self): #type: ignore
        return Trip.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TripDestroyApiView(generics.RetrieveDestroyAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    
    def get_queryset(self): # type: ignore
        return Trip.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can't DELETE this Trip")
        
        logger.info(f"User {self.request.user.pk} deleting trip: {instance.id}")
        print(f"Deleting trip: {instance}")
        instance.delete()
    
    def delete(self, request, *args, **kwargs):
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


class TripUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self): #type: ignore
        return Trip.objects.filter(user=self.request.user)


    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class LocationCreateApiView(generics.ListCreateAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self): #type: ignore
        return Location.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LocationDestroyUpdateApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer 
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self): #type: ignore
        return Location.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can't DELETE this Location")
        
        logger.info(f"User {self.request.user.pk} deleting location: {instance.id}")
        print(f"Deleting location: {instance}")
        instance.delete()


class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self): #type: ignore
        trip_id = self.kwargs['trip_id']
        return Expense.objects.filter(trip__id=trip_id, trip__user=self.request.user)

    def perform_create(self, serializer):
        trip_id = self.kwargs['trip_id']
        try:
            trip = Trip.objects.get(id=trip_id, user=self.request.user)
            serializer.save(trip=trip)
        except Trip.DoesNotExist:
            raise Http404("Trip not found")

class ExpneseUpdateApiView(generics.RetrieveDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self): # type: ignore
        return Expense.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can't DELETE this expense !")
        
        logger.info(f"user{self.request.user.pk} deleting expense: instance.id")
        print(f"Deleting expense: {instance}")
        instance.delete()
    
    def delete(self,request,*args, **kwargs):
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


class ExpenseUpdateApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self): #type: ignore
        return Expense.objects.filter(user=self.request.user)
    
    def perform_update(self,serializer):
        serializer.save(user=self.request.user)
