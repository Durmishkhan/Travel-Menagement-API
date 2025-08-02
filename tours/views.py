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
    ExpenseSerializer, ExpenseSummarySerializer, EmptySerializer
)
from .models import Trip, Location, Expense, ExpenseSummary
from .permissions import IsVisitor, IsGuideOwnerOrReadOnly, IsAdmin, TripPermission, LocationPermission, ExpensePermission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter

logger = logging.getLogger(__name__)
User = get_user_model()


class UserViewSet(viewsets.GenericViewSet):
    """User registration ViewSet"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TripViewSet(viewsets.ModelViewSet):
    """Trip CRUD operations ViewSet"""
    serializer_class = TripSerializer
    permission_classes = [TripPermission]
    filter_backends = [
        DjangoFilterBackend,   
        SearchFilter,          
        OrderingFilter,         
    ]
    
    filterset_fields = ['destination','user']
    search_fields = ['title', 'locations', 'start_date']   
    ordering_fields = ['budget', 'start_date']            
    ordering = ['start_date'] 
    
    def get_queryset(self): #type: ignore
        user = self.request.user

        if getattr(user,'role', None) == 'visitor':
            return Trip.objects.all()
        
        if not user.is_authenticated:
            return Trip.objects.none()
        
        if getattr(user, 'role', None) == 'admin':
            return Trip.objects.all()
        return Trip.objects.filter(user=user)
    
    def perform_create(self, serializer):
        trip = serializer.save(user=self.request.user)
        locations = self.request.POST.get('locations')  
        if locations:
            trip.locations.set(locations)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
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
        except PermissionDenied as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_403_FORBIDDEN
            )
        except Trip.DoesNotExist:
            return Response(
                {"error": "Trip not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "An error occurred while deleting the trip"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @action(detail=True, methods=['get'], url_path='summary')
    def summary(self,request,pk=None):
        trip = self.get_object()
        try:
            summary = trip.summary
        except ExpenseSummary.DoesNotExist:
            raise NotFound("Summary does not exist for this trip")
        serializer = ExpenseSummarySerializer(summary)
        return Response(serializer.data)
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsVisitor], serializer_class=EmptySerializer)
    def enroll(self, request, pk=None):
        trip = self.get_object()
        user = request.user

        if user in trip.enrolled_visitors.all():
            return Response({'detail': 'You are already enrolled in this trip.'}, status=status.HTTP_400_BAD_REQUEST)

        trip.enrolled_visitors.add(user)
        return Response({'detail': 'Successfully enrolled in this trip.'}, status=status.HTTP_200_OK)

class LocationViewSet(viewsets.ModelViewSet):
    """Location CRUD operations ViewSet"""
    serializer_class = LocationSerializer
    permission_classes = [LocationPermission]
    filter_backends = [
        DjangoFilterBackend,   
        SearchFilter,       
    ]
    
    filterset_fields = ['user']
    search_fields = ['title']   
    
    
    def get_queryset(self): #type: ignore
        user = self.request.user 
        if not user.is_authenticated:
            return Location.objects.none()
        if getattr(user, 'role', None) == 'admin':
            return Location.objects.all()
        if getattr(user, 'role', None) == 'visitor':
            return Location.objects.all()
        return Location.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
        logger.info(f"User {self.request.user.pk} deleting location: {instance.id}")
        print(f"Deleting location: {instance}")
        instance.delete()

    

class ExpenseViewSet(viewsets.ModelViewSet):
    """Expense CRUD operations ViewSet"""
    serializer_class = ExpenseSerializer
    permission_classes = [ExpensePermission]
    filter_backends = [
        DjangoFilterBackend,   
        SearchFilter,          
        OrderingFilter,         
    ]
    
    filterset_fields = ['category', 'trip', 'date']
    search_fields = ['description', 'trip__title']   
    ordering_fields = ['amount']            
    ordering = ['date']           
    
    def get_queryset(self): #type: ignore
        user = self.request.user
        trip_id = self.kwargs.get('trip_id')
        if not user.is_authenticated:
            return Expense.objects.none()
        if user.role == 'admin': #type: ignore
            if trip_id:
                return Expense.objects.filter(trip__id=trip_id)
            return Expense.objects.all()
        
        if user.role == 'guide': #type: ignore
            if trip_id:
                return Expense.objects.filter(trip__id=trip_id, trip__user=user)
            return Expense.objects.filter(trip__user=user)
        if trip_id:
            return Expense.objects.filter(trip__id=trip_id, user=user)
        return Expense.objects.filter(user=user)
    
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
        instance = serializer.instance
        serializer.save(trip=instance.trip, user=instance.user)
    
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
    serializer_class = ExpenseSummarySerializer
    permission_classes = [IsAuthenticated]
    queryset = ExpenseSummary.objects.all()
    
    def get_queryset(self):#type: ignore
        user = self.request.user
        if user.role in ['visitor', 'admin']: #type: ignore
            return ExpenseSummary.objects.all()
        return ExpenseSummary.objects.filter(trip__user=user)

    
    # @action(detail=True, methods=['get'], url_path='summary')
    # def summary(self, request, pk=None):
    #     try:
    #         summary = ExpenseSummary.objects.get(trip__id=pk, trip__user=request.user)
    #     except ExpenseSummary.DoesNotExist:
    #         raise Http404("Expense summary not found or permission denied.")
    #     serializer = self.get_serializer(summary)
    #     return Response(serializer.data)














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



