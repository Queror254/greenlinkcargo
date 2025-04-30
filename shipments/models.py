# shipments/models.py
from django.db import models
from clients.models import Client  # Import the Client model
from users.models import Business
import uuid
from datetime import datetime
from django.utils.timezone import now

class Invoice(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    shipment = models.OneToOneField('Shipment', on_delete=models.CASCADE)  
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(default=now)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.client.name}"



class Shipment(models.Model):
    SHIPMENT_TYPE_CHOICES = [
        ('air', 'Air'),
        ('sea', 'Sea')
    ]

    STATUS_CHOICES = [
        ('received', 'Received'),
        ('in_transit', 'In Transit'),
        ('cleared', 'Cleared'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)

    tracking_number = models.CharField(
        max_length=36, unique=True, default=uuid.uuid4, editable=False
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="shipments")
    shipment_type = models.CharField(max_length=10, choices=SHIPMENT_TYPE_CHOICES)
    airwaybill = models.CharField(max_length=20, blank=True, null=True)
    seawaybill = models.CharField(max_length=20, blank=True, null=True)
    weight = models.FloatField()
    volume = models.FloatField()
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    recepient_name = models.CharField(max_length=100, blank=True, null=True)
    recepient_phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    shipment_cost = models.FloatField(default=0.0, blank=True, null=True)
    status = models.CharField(max_length=200,)
    shipment_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def calculate_rate(self):
        base_rate = 50  # Flat rate
        weight_rate = self.weight * 10
        volume_rate = self.volume * 5
        return base_rate + weight_rate + volume_rate

    def save(self, *args, **kwargs):
        # Auto-generate the airwaybill or seawaybill if not provided
        current_year = datetime.now().year
        unique_part = str(self.tracking_number).split('-')[0].upper()
        if self.shipment_type == 'air' and not self.airwaybill:
            self.airwaybill = f"AWB-{current_year}-{unique_part}"
        elif self.shipment_type == 'sea' and not self.seawaybill:
            self.seawaybill = f"SWB-{current_year}-{unique_part}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Shipment {self.tracking_number} from {self.origin} to {self.destination} - {self.status.title()}"
