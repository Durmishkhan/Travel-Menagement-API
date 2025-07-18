from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Expense, ExpenseSummary
from decimal import Decimal

@receiver([post_save, post_delete], sender=Expense)
def update_expense_summary(sender, instance, **kwargs):
    trip = instance.trip
    total = trip.expenses.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
    breakdown = {
        category: Decimal(str(trip.expenses.filter(category=category).aggregate(total=models.Sum('amount'))['total'] or 0))
        for category, _ in Expense.CATEGORY_CHOICES
    }
    summary, _ = ExpenseSummary.objects.get_or_create(trip=trip)
    summary.total_amount = total
    summary.category_breakdown = breakdown
    summary.save()