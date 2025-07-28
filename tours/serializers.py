from rest_framework import serializers
from .models import User,Expense,Location,Trip,ExpenseSummary

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"

class TripSerializer(serializers.ModelSerializer):
    locations = serializers.SerializerMethodField()
    budget = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = ['id', 'title', 'destination', 'locations', 'start_date', 'end_date',
                  'budget', 'notes', 'user']

    def get_locations(self, obj):
        return [location.title for location in obj.locations.all()]

    def get_budget(self, obj):
        return f"{obj.budget} $"


class ExpenseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    trip = serializers.CharField(source='trip.title', read_only=True)
    amount = serializers.SerializerMethodField()
    class Meta:
        model = Expense
        fields = ['id', 'trip', 'category_display', 'amount', 'description', 'date', 'user']
    def get_amount(self,obj):
        return f"{obj.amount} $"

class ExpenseSummarySerializer(serializers.ModelSerializer):
    trip = serializers.CharField(source='trip.title', read_only=True)
    total_amount = serializers.SerializerMethodField()
    category_breakdown = serializers.SerializerMethodField()
    class Meta:
        model = ExpenseSummary
        fields = ['id', 'trip', 'total_amount', 'category_breakdown', 'generated_at']
        read_only_fields = ['id', 'generated_at']

    def get_total_amount(self,obj):
        return f"{obj.total_amount} $"
    def get_category_breakdown(self, obj):
        breakdown = obj.category_breakdown
        return {
            key: f"{value} $" for key, value in breakdown.items()
        }
    