from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

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

    def __str__(self):
        category_display = dict(self.CATEGORY_CHOICES).get(self.category, self.category)
        return f"{category_display} - {self.amount} ({self.date})"
