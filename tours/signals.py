from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Expense, ExpenseSummary
from decimal import Decimal

@receiver([post_save, post_delete], sender=Expense)
def update_expense_summary(sender, instance, **kwargs):
    trip = instance.trip
    total = trip.expenses.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
    
    # Decimal-ების float-ად კონვერტაცია JSON-ისთვის
    breakdown = {}
    for category, _ in Expense.CATEGORY_CHOICES:
        category_total = trip.expenses.filter(category=category).aggregate(
            total=models.Sum('amount')
        )['total']
        
        # Decimal-ის float-ად კონვერტაცია
        breakdown[category] = float(category_total) if category_total else 0.0
    
    summary, _ = ExpenseSummary.objects.get_or_create(trip=trip)
    summary.total_amount = total
    summary.category_breakdown = breakdown  # ახლა float-ებია, არა Decimal-ები
    summary.save()