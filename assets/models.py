from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import BaseModel, Company
from users.models import Department, Location
import uuid


class AssetCategory(BaseModel):
    """Main asset categories"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='asset_categories')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_categories')
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Icon class or name")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'asset_categories'
        ordering = ['company', 'name']
        verbose_name = 'Asset Category'
        verbose_name_plural = 'Asset Categories'
        unique_together = [['company', 'code'], ['company', 'name']]

    def __str__(self):
        if self.company:
            return f"{self.company.code} - {self.code} - {self.name}"
        return f"{self.code} - {self.name}"


class AssetType(BaseModel):
    """Specific asset types under categories"""
    CATEGORY_CHOICES = [
        ('ELECTRONIC', 'Electronic Assets'),
        ('IT_TECH', 'IT & Technology Assets'),
        ('FURNITURE', 'Furniture & Office Assets'),
        ('MACHINERY', 'Plant, Machinery & Industrial Assets'),
        ('FACILITY', 'Facility & Infrastructure Assets'),
        ('VEHICLE', 'Vehicles & Transportation Assets'),
        ('SOFTWARE', 'Software & Intangible Assets'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='asset_types')
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE, related_name='asset_types')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    requires_calibration = models.BooleanField(default=False)
    requires_insurance = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'asset_types'
        ordering = ['company', 'category', 'name']
        verbose_name = 'Asset Type'
        verbose_name_plural = 'Asset Types'
        unique_together = [['company', 'code'], ['company', 'name']]

    def __str__(self):
        if self.company:
            return f"{self.company.code} - {self.code} - {self.name}"
        return f"{self.code} - {self.name}"


class Vendor(BaseModel):
    """Vendor/Supplier information"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vendors')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='India')
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True, verbose_name='GSTIN')
    pan = models.CharField(max_length=10, blank=True, null=True, verbose_name='PAN')
    vendor_type = models.CharField(max_length=50, choices=[
        ('SUPPLIER', 'Supplier'),
        ('MANUFACTURER', 'Manufacturer'),
        ('SERVICE_PROVIDER', 'Service Provider'),
        ('CONTRACTOR', 'Contractor'),
    ], default='SUPPLIER')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'vendors'
        ordering = ['company', 'name']
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        unique_together = [['company', 'code'], ['company', 'name']]

    def __str__(self):
        if self.company:
            return f"{self.company.code} - {self.code} - {self.name}"
        return f"{self.code} - {self.name}"


class Asset(BaseModel):
    """Main asset model"""
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('ORDERED', 'Ordered'),
        ('IN_STOCK', 'In Stock'),
        ('DEPLOYED', 'Deployed'),
        ('IN_USE', 'In Use'),
        ('UNDER_MAINTENANCE', 'Under Maintenance'),
        ('RETIRED', 'Retired'),
        ('DISPOSED', 'Disposed'),
        ('LOST', 'Lost'),
        ('STOLEN', 'Stolen'),
    ]

    CONDITION_CHOICES = [
        ('EXCELLENT', 'Excellent'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
        ('NOT_WORKING', 'Not Working'),
    ]

    # Company
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='assets')
    
    # Basic Information
    asset_tag = models.CharField(max_length=100, db_index=True, help_text="Unique asset identifier")
    qr_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, help_text="QR Code UUID")
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    
    # Asset Classification
    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT, related_name='assets')
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name='assets')
    
    # Asset Details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    make = models.CharField(max_length=100, blank=True, null=True, verbose_name='Manufacturer/Make')
    model = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    specifications = models.TextField(blank=True, null=True, help_text="Technical specifications")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='GOOD', blank=True, null=True)
    
    # Location & Assignment
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets')
    custodian = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='custodian_assets')
    
    # Procurement Information
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='supplied_assets')
    purchase_order_number = models.CharField(max_length=100, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    
    # Warranty Information
    warranty_start_date = models.DateField(blank=True, null=True)
    warranty_end_date = models.DateField(blank=True, null=True)
    warranty_period_months = models.IntegerField(blank=True, null=True, help_text="Warranty period in months")
    
    # AMC Information
    amc_vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='amc_assets')
    amc_start_date = models.DateField(blank=True, null=True, verbose_name='AMC Start Date')
    amc_end_date = models.DateField(blank=True, null=True, verbose_name='AMC End Date')
    amc_cost = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))], verbose_name='AMC Cost')
    
    # Depreciation
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Annual depreciation rate (%)")
    salvage_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    useful_life_years = models.IntegerField(blank=True, null=True, help_text="Expected useful life in years")
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    is_critical = models.BooleanField(default=False, help_text="Is this a critical asset?")
    is_insured = models.BooleanField(default=False)
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True)
    insurance_expiry_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'assets'
        ordering = ['company', '-created_at']
        verbose_name = 'Asset'
        verbose_name_plural = 'Assets'
        unique_together = [['company', 'asset_tag']]
        indexes = [
            models.Index(fields=['company', 'asset_tag']),
            models.Index(fields=['company', 'serial_number']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['company', 'location', 'department']),
        ]

    def __str__(self):
        if self.company:
            return f"{self.company.code} - {self.asset_tag} - {self.name}"
        return f"{self.asset_tag} - {self.name}"

    @property
    def is_under_warranty(self):
        """Check if asset is currently under warranty"""
        if self.warranty_end_date:
            from django.utils import timezone
            return timezone.now().date() <= self.warranty_end_date
        return False

    @property
    def is_under_amc(self):
        """Check if asset is currently under AMC"""
        if self.amc_end_date:
            from django.utils import timezone
            return timezone.now().date() <= self.amc_end_date
        return False


class AssetDocument(BaseModel):
    """Documents related to assets (invoices, manuals, certificates, etc.)"""
    DOCUMENT_TYPES = [
        ('INVOICE', 'Invoice'),
        ('PURCHASE_ORDER', 'Purchase Order'),
        ('WARRANTY_CARD', 'Warranty Card'),
        ('AMC_CONTRACT', 'AMC Contract'),
        ('USER_MANUAL', 'User Manual'),
        ('CERTIFICATE', 'Certificate'),
        ('INSURANCE', 'Insurance Document'),
        ('OTHER', 'Other'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    document_file = models.FileField(upload_to='asset_documents/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')

    class Meta:
        db_table = 'asset_documents'
        ordering = ['-created_at']
        verbose_name = 'Asset Document'
        verbose_name_plural = 'Asset Documents'

    def __str__(self):
        if self.asset:
            return f"{self.asset.asset_tag} - {self.title}"
        return self.title


class AssetHistory(models.Model):
    """Track all changes and movements of assets"""
    ACTION_TYPES = [
        ('CREATED', 'Created'),
        ('UPDATED', 'Updated'),
        ('ASSIGNED', 'Assigned'),
        ('TRANSFERRED', 'Transferred'),
        ('RETURNED', 'Returned'),
        ('MAINTENANCE', 'Sent for Maintenance'),
        ('REPAIRED', 'Repaired'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('LOCATION_CHANGED', 'Location Changed'),
        ('DISPOSED', 'Disposed'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='history')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_date = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='asset_actions')
    
    old_value = models.TextField(blank=True, null=True, help_text="Previous value (JSON)")
    new_value = models.TextField(blank=True, null=True, help_text="New value (JSON)")
    
    from_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets_from')
    to_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets_to')
    
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets_given')
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets_received')
    
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'asset_history'
        ordering = ['-action_date']
        verbose_name = 'Asset History'
        verbose_name_plural = 'Asset History'

    def __str__(self):
        if self.asset:
            return f"{self.asset.asset_tag} - {self.action_type} on {self.action_date}"
        return f"{self.action_type} on {self.action_date}"


class AssetTransfer(BaseModel):
    """
    Asset transfer request and approval workflow.
    Formal process for transferring assets between users/locations.
    """
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending Approval'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE, related_name='transfers')
    transfer_number = models.CharField(max_length=50, unique=True)
    
    # From details
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_from')
    from_location = models.ForeignKey('users.Location', on_delete=models.SET_NULL, null=True, related_name='transfers_from')
    from_department = models.ForeignKey('users.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_from')
    
    # To details
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_to')
    to_location = models.ForeignKey('users.Location', on_delete=models.SET_NULL, null=True, related_name='transfers_to')
    to_department = models.ForeignKey('users.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers_to')
    
    # Request details
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfer_requests')
    requested_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    
    # Approval workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfer_approvals')
    approval_date = models.DateTimeField(null=True, blank=True)
    approval_remarks = models.TextField(blank=True)
    
    # Completion
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfer_completions')
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Documents
    transfer_document = models.FileField(upload_to='transfer_documents/', null=True, blank=True)
    
    class Meta:
        db_table = 'asset_transfers'
        ordering = ['-requested_date']
        verbose_name = 'Asset Transfer'
        verbose_name_plural = 'Asset Transfers'
        indexes = [
            models.Index(fields=['status', '-requested_date']),
            models.Index(fields=['asset', '-requested_date']),
        ]
    
    def __str__(self):
        if self.asset:
            return f"{self.transfer_number} - {self.asset.asset_tag}"
        return self.transfer_number or "New Transfer"
    
    def save(self, *args, **kwargs):
        if not self.transfer_number:
            # Generate unique transfer number
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_transfer = AssetTransfer.objects.filter(
                transfer_number__startswith=f'TRF-{date_str}'
            ).order_by('-transfer_number').first()
            
            if last_transfer:
                last_num = int(last_transfer.transfer_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.transfer_number = f'TRF-{date_str}-{new_num:04d}'
        
        super().save(*args, **kwargs)


class AssetDisposal(BaseModel):
    """
    Asset disposal request and approval workflow.
    Formal process for disposing/writing off assets.
    """
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending Approval'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    SELL = 'SELL'
    SCRAP = 'SCRAP'
    DONATE = 'DONATE'
    DESTROY = 'DESTROY'
    RETURN_TO_VENDOR = 'RETURN_TO_VENDOR'
    
    METHOD_CHOICES = [
        (SELL, 'Sell'),
        (SCRAP, 'Scrap'),
        (DONATE, 'Donate'),
        (DESTROY, 'Destroy'),
        (RETURN_TO_VENDOR, 'Return to Vendor'),
    ]
    
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE, related_name='disposals')
    disposal_number = models.CharField(max_length=50, unique=True)
    
    # Request details
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='disposal_requests')
    requested_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    disposal_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    
    # Financial details
    current_book_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    disposal_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    disposal_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Approval workflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='disposal_approvals')
    approval_date = models.DateTimeField(null=True, blank=True)
    approval_remarks = models.TextField(blank=True)
    
    # Completion
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='disposal_completions')
    completed_date = models.DateTimeField(null=True, blank=True)
    buyer_details = models.TextField(blank=True, help_text='Buyer information if sold')
    
    # Documents
    disposal_document = models.FileField(upload_to='disposal_documents/', null=True, blank=True)
    
    class Meta:
        db_table = 'asset_disposals'
        ordering = ['-requested_date']
        verbose_name = 'Asset Disposal'
        verbose_name_plural = 'Asset Disposals'
        indexes = [
            models.Index(fields=['status', '-requested_date']),
            models.Index(fields=['asset', '-requested_date']),
        ]
    
    def __str__(self):
        if self.asset:
            return f"{self.disposal_number} - {self.asset.asset_tag}"
        return self.disposal_number or "New Disposal"
    
    def save(self, *args, **kwargs):
        if not self.disposal_number:
            # Generate unique disposal number
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_disposal = AssetDisposal.objects.filter(
                disposal_number__startswith=f'DSP-{date_str}'
            ).order_by('-disposal_number').first()
            
            if last_disposal:
                last_num = int(last_disposal.disposal_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.disposal_number = f'DSP-{date_str}-{new_num:04d}'
        
        super().save(*args, **kwargs)
