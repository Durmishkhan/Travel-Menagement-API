from django.contrib import admin
from .models import User, Trip, Location, Expense, ExpenseSummary

admin.site.register(User)
admin.site.register(Trip)
admin.site.register(Location)
admin.site.register(Expense)
admin.site.register(ExpenseSummary)
