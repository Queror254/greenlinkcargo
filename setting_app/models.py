from django.db import models
from users.models import Business

class Rates(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
    weight_rate = models.FloatField(verbose_name="Rate per Kilogram")
    cbm_rate = models.FloatField(verbose_name="Rate per Cubic Meter")

    def __str__(self):
        return f"Weight Rate: {self.weight_rate}, CBM Rate: {self.cbm_rate}"
