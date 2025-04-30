from django.db import models
from users.models import CustomUser, Business
from shipments.models import Shipment

class Payment(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50, default="Cash")

    def __str__(self):
        return f"Payment for {self.shipment} - {self.amount}"


class Credit(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
    client = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Credit for {self.client} - Balance: {self.outstanding_balance}"
