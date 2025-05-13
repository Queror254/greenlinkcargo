from django.db import models
from users.models import Business
from shipments.models import Shipment

class Rates(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
    weight_rate = models.FloatField(verbose_name="Rate per Kilogram")
    cbm_rate = models.FloatField(verbose_name="Rate per Cubic Meter")

    def __str__(self):
        return f"Weight Rate: {self.weight_rate}, CBM Rate: {self.cbm_rate}"
    
class Taxes(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='Tax percentage',
        help_text='Enter the tax rate as a percentage, e.g., 16.00 for 16%'
    )
    
class Additionalcosts(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    value = models.DecimalField(max_digits=20, decimal_places=2)
