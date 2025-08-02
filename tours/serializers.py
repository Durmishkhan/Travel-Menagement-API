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
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Location
        fields = "__all__"

class TripSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    locations = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Location.objects.all()
    )
    locations_display = serializers.SerializerMethodField(read_only=True)

    budget = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = ['id', 'title', 'destination', 'locations', 'locations_display',
                  'start_date', 'end_date', 'budget', 'notes', 'user']

    def get_locations_display(self, obj):
        return [location.title for location in obj.locations.all()]

    def get_budget(self, obj):
        return f"{obj.budget} $"



class ExpenseSerializer(serializers.ModelSerializer):
    trip_title = serializers.CharField(source='trip.title', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)  # რომ მიიღოს POST
    trip = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Expense
        fields = [
            'id', 'trip', 'trip_title', 'category', 'category_display',
            'amount', 'description', 'date', 'user'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['amount'] = f"{data['amount']} $"
        return data


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
    

