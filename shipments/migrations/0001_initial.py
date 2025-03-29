# Generated by Django 5.1.7 on 2025-03-27 11:12

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tracking_number', models.CharField(default=uuid.uuid4, editable=False, max_length=36, unique=True)),
                ('shipment_type', models.CharField(choices=[('air', 'Air'), ('sea', 'Sea')], max_length=10)),
                ('airwaybill', models.CharField(blank=True, max_length=20, null=True)),
                ('seawaybill', models.CharField(blank=True, max_length=20, null=True)),
                ('weight', models.FloatField()),
                ('volume', models.FloatField()),
                ('origin', models.CharField(max_length=100)),
                ('destination', models.CharField(max_length=100)),
                ('estimated_delivery', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('received', 'Received'), ('in_transit', 'In Transit'), ('cleared', 'Cleared'), ('ready_for_pickup', 'Ready for Pickup'), ('delivered', 'Delivered')], default='received', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ShipmentStatusHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('received', 'Received'), ('in_transit', 'In Transit'), ('cleared', 'Cleared'), ('ready_for_pickup', 'Ready for Pickup'), ('delivered', 'Delivered')], max_length=20)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('shipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='shipments.shipment')),
            ],
        ),
    ]
