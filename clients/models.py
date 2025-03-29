from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=191)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    postalcode = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.name