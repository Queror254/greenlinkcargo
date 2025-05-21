# shipments/models.py
from django.db import models
from clients.models import Client  # Import the Client model
from users.models import Business
import uuid
from datetime import datetime
from django.utils.timezone import now
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.db.models import Sum
from decimal import Decimal




class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('overdue', 'Overdue'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, blank=True, null=True)
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    shipment = models.OneToOneField('Shipment', on_delete=models.CASCADE, related_name='invoice')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    issued_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    @property
    def shipment_cost(self):
        """Returns the actual shipment cost from the associated shipment"""
        return self.shipment.shipment_cost or self.shipment.calculate_rate
    
    
    def save(self, *args, **kwargs):
        from setting_app.models import Taxes
        tax = Taxes.objects.first();
        if tax:
            tax_rate = tax.rate / 100
        else : 
            tax_rate = 0.1 #10% tax
            
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Ensure financial fields are in sync with shipment
        if not self.subtotal or not self.total_amount:
            self.subtotal = self.shipment_cost
            self.tax_amount = self.subtotal * tax_rate
            self.total_amount = self.subtotal + self.tax_amount
            
        super().save(*args, **kwargs)
        
    def update_payment_status(self):
        """Automatically determine the correct payment status"""
        total_paid = sum(payment.amount for payment in self.payments.all())
        
        if total_paid >= self.total_amount:
            self.payment_status = 'paid'
        elif total_paid > 0:
            self.payment_status = 'partial'
        elif self.due_date and timezone.now().date() > self.due_date:
            self.payment_status = 'overdue'
        else:
            self.payment_status = 'pending'
        
        self.save(update_fields=['payment_status'])
    
    @property
    def balance_due(self):
        return max(self.total_amount - sum(p.amount for p in self.payments.all()), 0)
    
    def get_absolute_url(self):
        return reverse('invoice_detail', kwargs={'pk': self.pk})
        
    @property
    def amount_paid(self):  
        return sum(payment.amount for payment in self.payments.all())

    #@property
    #def balance_due(self):
    #    return self.total_amount - self.amount_paid

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.client.name}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
        ('card', 'Credit Card'),
        ('other', 'Other'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateTimeField(default=timezone.now)
    method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')
    reference = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update invoice status and verify payment doesn't exceed balance
        if self.amount > self.invoice.balance_due:
            raise ValueError("Payment amount exceeds invoice balance")
        
        self.invoice.update_payment_status()
    
    def __str__(self):
        return f"Payment of ${self.amount} for {self.invoice}"


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
    quantity = models.CharField(max_length=150, blank=True, null=True)
    weight = models.FloatField()
    volume = models.FloatField()
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    recepient_name = models.CharField(max_length=100, blank=True, null=True)
    recepient_phone = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)
    shipment_cost = models.DecimalField(
        max_digits=10,  # Max total digits (including decimals)
        decimal_places=2,  # Number of decimal places (e.g., 2 for cents)
        default=Decimal('0.00')
    )
    status = models.CharField(max_length=200,)
    shipment_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def calculate_rate(self):
        from setting_app.models import Additionalcosts, Rates
        
        # Initialize with default rates
        default_rates = {
            'weight_rate': Decimal('10.00'),
            'cbm_rate': Decimal('5.00')
        }
        rates = Rates(**default_rates)
        
        try:            
            # Check for route-specific rates
            if self.origin == 'Dubai':
                route_name = 'DubaiKE'
                rates = Rates.objects.get(business=self.business, route=route_name)
                
            elif self.origin == 'Turkey':
                route_name = 'TurkeyKE'
                rates = Rates.objects.get(business=self.business, route=route_name)
            
            else:
                route_name = "default"
                rates = Rates.objects.get(business=self.business, route=route_name)
                
                
        except Rates.DoesNotExist:
            pass  # Keep the initialized rates
        
        # Convert all values to Decimal for calculations
        weight = Decimal(str(self.weight))
        volume = Decimal(str(self.volume))
        
        # Calculate base rates
        weight_rate = weight * rates.weight_rate
        volume_rate = volume * rates.cbm_rate
        
        # Calculate additional costs
        additional_costs = Decimal('0.00')
        cost_aggregate = Additionalcosts.objects.filter(
            shipment=self
        ).aggregate(
            total=Sum('value')
        )['total']
        
        if cost_aggregate is not None:
            additional_costs = Decimal(str(cost_aggregate))
        
        # Return appropriate rate based on shipment type
        if self.shipment_type == 'air':
            return (weight_rate + additional_costs).quantize(Decimal('0.00'))
        return (volume_rate + additional_costs).quantize(Decimal('0.00'))

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
    
    def create_invoice(self):
        if not hasattr(self, 'invoice'):
            # Convert all values to Decimal for invoice calculations
            calculated_rate = Decimal(str(self.calculate_rate))
            manual_cost = Decimal(str(self.shipment_cost or 0))
            
            # Use the higher of calculated rate or manual cost
            subtotal = max(calculated_rate, manual_cost)
            
            from setting_app.models import Taxes
            try:
                tax = Taxes.objects.first()
                tax_rate = Decimal(str(tax.rate)) / Decimal('100') if tax else Decimal('0.10')
            except Exception:
                tax_rate = Decimal('0.10')  # 10% as fallback
            
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount
            
            return Invoice.objects.create(
                business=self.business,
                shipment=self,
                client=self.client,
                subtotal=subtotal,
                tax_amount=tax_amount,
                total_amount=total_amount,
                due_date=timezone.now() + timezone.timedelta(days=30)
            )
        return self.invoice