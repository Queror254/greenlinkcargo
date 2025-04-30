from django.db import models
from users.models import Business, Branch

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=191)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    postalcode = models.CharField(max_length=20, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-assign business if staff belongs to a branch
        if self.branch and not self.business:
            self.business = self.branch.business
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name