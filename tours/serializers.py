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

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = "__all__"

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"

class ExpenseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'trip', 'category', 'category_display', 'amount', 'description', 'date']

class ExpenseSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseSummary
        fields = ['id', 'trip', 'total_amount', 'category_breakdown', 'generated_at']
        read_only_fields = ['id', 'generated_at']
