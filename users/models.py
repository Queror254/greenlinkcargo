from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError


# Custom user model, extending AbstractUser.
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True)
    business = models.ForeignKey(
        'Business',
        on_delete=models.CASCADE,
        related_name='employees',
        null=True,
        blank=True
    )
    
    def clean(self):
        """Validate business logic before saving"""
        if self.role == 'staff' and not self.branch:
            raise ValidationError("Staff must be assigned to a branch.")
        
        if self.branch and self.branch.business != self.business:
            raise ValidationError("Selected branch does not belong to this business.")
    
    def save(self, *args, **kwargs):
        # Auto-assign business if staff belongs to a branch
        if self.branch and not self.business:
            self.business = self.branch.business
        super().save(*args, **kwargs)
    
    # NOTE: AbstractUser already provides first_name and last_name.
    def __str__(self):
        return f"{self.username} - {self.role}"


# Choices for accounting methods
ACCOUNTING_METHOD_CHOICES = (
    ('fifo', 'FIFO (First In First Out)'),
    ('lifo', 'LIFO (Last In First Out)'),
)

class Business(models.Model):
    # --- Business Details ---
    name = models.CharField(max_length=191)
    start_date = models.DateField(blank=True, null=True)
    
    # Here we use an integer field to represent the selected currency id.
    currency_id = models.PositiveIntegerField()
    
    business_logo = models.ImageField(
    upload_to='images/business_logos/',
    blank=True,
    null=True,
    help_text="Upload your business logo"
)
    
    website = models.URLField(blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    alternate_number = models.CharField(max_length=20, blank=True, null=True)
    
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    landmark = models.CharField(max_length=100)
    time_zone = models.CharField(max_length=100)
    
    # --- Business Settings ---
    tax_label_1 = models.CharField(max_length=50, blank=True, null=True)
    tax_number_1 = models.CharField(max_length=50, blank=True, null=True)
    tax_label_2 = models.CharField(max_length=50, blank=True, null=True)
    tax_number_2 = models.CharField(max_length=50, blank=True, null=True)
    fy_start_month = models.PositiveSmallIntegerField(help_text="Month number (1 for January, etc.)")
    accounting_method = models.CharField(
        max_length=4, 
        choices=ACCOUNTING_METHOD_CHOICES, 
        default='fifo'
    )
    
    # --- Owner Information ---
    # This links the business to its owner user. The owner’s id is automatically stored in owner_id.
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_business'
    )
    # Additionally, store the owner's email.
    owner_email = models.EmailField(blank=True, null=True, editable=False)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Automatically update owner_email when saving.
        if self.owner:
            self.owner_email = self.owner.email
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Branch(models.Model):
    # --- Business Details ---
    name = models.CharField(max_length=191)    
    # Here we use an integer field to represent the selected currency id.
    currency_id = models.PositiveIntegerField()
    mobile = models.CharField(max_length=20, blank=True, null=True)
    alternate_number = models.CharField(max_length=20, blank=True, null=True)
    
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    landmark = models.CharField(max_length=100)
    time_zone = models.CharField(max_length=100)    
    # --- Owner Information ---
    # This links the branch to its main business.
    business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='branches')
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name