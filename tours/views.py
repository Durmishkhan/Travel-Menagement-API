from django.contrib.auth import get_user_model
from rest_framework import generics
from .serializers import UserSerializer, TripSerializer, LocationsSerialzier, ExpenseSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Trip,Locations,Expense

User = get_user_model()

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class TripListCreate(generics.ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):  # type: ignore
        return Trip.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




