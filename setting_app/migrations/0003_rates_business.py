# Generated by Django 5.1.7 on 2025-04-28 09:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting_app', '0002_alter_rates_cbm_rate_alter_rates_weight_rate'),
        ('users', '0007_customuser_business_alter_business_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='rates',
            name='business',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.business'),
        ),
    ]
