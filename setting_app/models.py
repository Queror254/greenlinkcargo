from django.db import models
from users.models import Business
from shipments.models import Shipment

#Shipping rates models
class Rates(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
    route = models.CharField(max_length=100, null=True, blank=True)
    weight_rate = models.DecimalField(max_digits=10, decimal_places=2)
    cbm_rate = models.DecimalField(max_digits=10, decimal_places=2)
    #remember to change this fields during migration
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,  null=True, blank=True)

    def __str__(self):
        return f"{self.route} - ${self.weight_rate}/kg, ${self.cbm_rate}/m³"

    class Meta:
        verbose_name_plural = "Shipping Rates"
        
#Tax model     
class Taxes(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name='Tax percentage',
        help_text='Enter the tax rate as a percentage, e.g., 16.00 for 16%'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,  null=True, blank=True)
    
class Additionalcosts(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,  null=True, blank=True)
