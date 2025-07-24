from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from decimal import Decimal

class User(AbstractUser):
    ROLE_CHOICES = [
        ('visitor', 'Visitor'),
        ('guide', 'Guide'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='visitor')

    def __str__(self):
        role_display = dict(self.ROLE_CHOICES).get(self.role, self.role)
        return f"{self.username} ({role_display})"



class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    locations = models.ManyToManyField('Location', related_name='trips', blank=True)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be earlier than start date.")

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='end_date_gte_start_date'
            )
        ]
    def __str__(self):
        return self.title
class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    open_time= models.TimeField()
    close_time = models.TimeField()
    description = models.TextField(blank = True)

    def __str__(self):
        return self.title

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('transport', 'Transport'),
        ('accommodation', 'Accommodation'),
        ('food', 'Food'),
        ('activity', 'Activity'),
        ('other', 'Other'),
    ]

    trip = models.ForeignKey('Trip', related_name='expenses', on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def clean(self):
        if not (self.trip.start_date <= self.date <= self.trip.end_date):
            raise ValidationError("Expense date must be within the trip's date range.")

    def __str__(self):
        category_display = dict(self.CATEGORY_CHOICES).get(self.category, self.category)
        return f"{category_display} - {self.amount} ({self.date})"

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gt=0), name='positive_amount')
        ]

def validate_category_breakdown(value):
    if not isinstance(value, dict):
        raise ValidationError("category_breakdown must be a dictionary.")
    for key, val in value.items():
        if not isinstance(val, (int, float)) or val < 0:
            raise ValidationError("Category values must be positive numbers.")

class ExpenseSummary(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='summary')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default= Decimal('0'))
    category_breakdown = models.JSONField(validators=[validate_category_breakdown], blank= True, default=dict)
    generated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"Summary for {self.trip.title}"