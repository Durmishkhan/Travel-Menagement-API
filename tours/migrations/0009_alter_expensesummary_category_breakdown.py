# Generated by Django 5.2.4 on 2025-07-22 12:09

import tours.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0008_alter_expensesummary_total_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expensesummary',
            name='category_breakdown',
            field=models.JSONField(blank=True, validators=[tours.models.validate_category_breakdown]),
        ),
    ]
