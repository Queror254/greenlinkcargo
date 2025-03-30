from django.db import models

class Rates(models.Model):
    weight_rate = models.FloatField(verbose_name="Rate per Kilogram")
    cbm_rate = models.FloatField(verbose_name="Rate per Cubic Meter")

    def __str__(self):
        return f"Weight Rate: {self.weight_rate}, CBM Rate: {self.cbm_rate}"
