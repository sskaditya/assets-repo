from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    An abstract base class model that provides soft delete functionality.
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Soft delete the object"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore a soft deleted object"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Base model that combines timestamp and soft delete functionality.
    Use this as the base for most models in the application.
    """
    class Meta:
        abstract = True


class Company(BaseModel):
    """
    Company/Tenant model for multi-company support.
    Softlogic super admin can create multiple companies.
    """
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True, help_text="Unique company code")
    
    # Contact Information
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Sri Lanka')
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Tax Information
    tax_id = models.CharField(max_length=50, blank=True, null=True, help_text="Tax ID / Business Registration Number")
    gstin = models.CharField(max_length=20, blank=True, null=True, verbose_name='GSTIN')
    
    # Branding
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    subscription_start_date = models.DateField(blank=True, null=True)
    subscription_end_date = models.DateField(blank=True, null=True)
    
    # Limits (optional - for subscription management)
    max_users = models.IntegerField(default=50, help_text="Maximum number of users allowed")
    max_assets = models.IntegerField(default=1000, help_text="Maximum number of assets allowed")
    
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'companies'
        ordering = ['name']
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_subscription_active(self):
        """Check if company subscription is active"""
        if not self.subscription_end_date:
            return True
        from django.utils import timezone
        return timezone.now().date() <= self.subscription_end_date
