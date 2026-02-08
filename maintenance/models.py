from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from core.models import BaseModel, Company
from assets.models import Asset, Vendor


class MaintenanceType(BaseModel):
    """Types of maintenance activities"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='maintenance_types')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'maintenance_types'
        ordering = ['company', 'name']
        verbose_name = 'Maintenance Type'
        verbose_name_plural = 'Maintenance Types'
        unique_together = [['company', 'code'], ['company', 'name']]

    def __str__(self):
        if self.company:
            return f"{self.company.code} - {self.code} - {self.name}"
        return f"{self.code} - {self.name}"


class MaintenanceSchedule(BaseModel):
    """Preventive maintenance schedules for assets"""
    FREQUENCY_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('HALF_YEARLY', 'Half Yearly'),
        ('YEARLY', 'Yearly'),
        ('CUSTOM', 'Custom'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_schedules')
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.PROTECT, related_name='schedules')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    interval_days = models.IntegerField(help_text="Interval in days (for custom frequency)", blank=True, null=True)
    
    start_date = models.DateField()
    next_due_date = models.DateField(help_text="Next scheduled maintenance date")
    last_completed_date = models.DateField(blank=True, null=True)
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_schedules')
    
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    estimated_duration_hours = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True, help_text="Estimated duration in hours")
    
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    send_reminder = models.BooleanField(default=True, help_text="Send reminder notifications?")
    reminder_days_before = models.IntegerField(default=7, help_text="Days before due date to send reminder")

    class Meta:
        db_table = 'maintenance_schedules'
        ordering = ['next_due_date']
        verbose_name = 'Maintenance Schedule'
        verbose_name_plural = 'Maintenance Schedules'

    def __str__(self):
        if self.asset and self.maintenance_type:
            return f"{self.asset.asset_tag} - {self.maintenance_type.name} (Due: {self.next_due_date})"
        elif self.asset:
            return f"{self.asset.asset_tag} (Due: {self.next_due_date})"
        return f"Schedule (Due: {self.next_due_date})"


class MaintenanceRequest(BaseModel):
    """Breakdown/ad-hoc maintenance requests"""
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('REJECTED', 'Rejected'),
    ]

    REQUEST_TYPES = [
        ('BREAKDOWN', 'Breakdown'),
        ('PREVENTIVE', 'Preventive'),
        ('CALIBRATION', 'Calibration'),
        ('INSPECTION', 'Inspection'),
        ('UPGRADE', 'Upgrade'),
        ('OTHER', 'Other'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='maintenance_requests')
    request_number = models.CharField(max_length=50, editable=False, db_index=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_requests')
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.PROTECT, related_name='requests')
    
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES, default='BREAKDOWN')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_maintenance')
    requested_date = models.DateTimeField(auto_now_add=True)
    
    issue_description = models.TextField()
    impact_description = models.TextField(blank=True, null=True, help_text="Impact on operations")
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_maintenance')
    approved_date = models.DateTimeField(blank=True, null=True)
    
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance_requests')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_requests')
    
    scheduled_date = models.DateField(blank=True, null=True)
    started_date = models.DateTimeField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    
    downtime_hours = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True, help_text="Asset downtime in hours")
    
    resolution_notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'maintenance_requests'
        ordering = ['company', '-requested_date']
        verbose_name = 'Maintenance Request'
        verbose_name_plural = 'Maintenance Requests'
        unique_together = [['company', 'request_number']]

    def __str__(self):
        parts = []
        if self.company:
            parts.append(self.company.code)
        if self.request_number:
            parts.append(self.request_number)
        if self.asset:
            parts.append(self.asset.asset_tag)
        return " - ".join(parts) if parts else "New Maintenance Request"

    def save(self, *args, **kwargs):
        if not self.request_number:
            # Generate request number
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_request = MaintenanceRequest.objects.filter(
                company=self.company,
                request_number__startswith=f'MR{date_str}'
            ).order_by('-request_number').first()
            
            if last_request:
                last_seq = int(last_request.request_number[-4:])
                new_seq = last_seq + 1
            else:
                new_seq = 1
            
            self.request_number = f'MR{date_str}{new_seq:04d}'
        
        super().save(*args, **kwargs)


class MaintenanceLog(BaseModel):
    """Log of maintenance activities performed"""
    maintenance_request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='logs', blank=True, null=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.PROTECT, related_name='logs')
    
    maintenance_date = models.DateField()
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='performed_maintenance')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_logs')
    
    work_description = models.TextField()
    parts_replaced = models.TextField(blank=True, null=True)
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    
    duration_hours = models.DecimalField(max_digits=5, decimal_places=1, help_text="Duration in hours")
    
    next_maintenance_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'maintenance_logs'
        ordering = ['-maintenance_date']
        verbose_name = 'Maintenance Log'
        verbose_name_plural = 'Maintenance Logs'

    def __str__(self):
        if self.asset and self.maintenance_type:
            return f"{self.asset.asset_tag} - {self.maintenance_type.name} on {self.maintenance_date}"
        elif self.asset:
            return f"{self.asset.asset_tag} on {self.maintenance_date}"
        return f"Maintenance on {self.maintenance_date}"


class MaintenanceDocument(BaseModel):
    """Documents related to maintenance activities"""
    DOCUMENT_TYPES = [
        ('WORK_ORDER', 'Work Order'),
        ('INVOICE', 'Invoice'),
        ('REPORT', 'Report'),
        ('CHECKLIST', 'Checklist'),
        ('PHOTO', 'Photo'),
        ('VIDEO', 'Video'),
        ('OTHER', 'Other'),
    ]

    maintenance_request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    maintenance_log = models.ForeignKey(MaintenanceLog, on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    document_file = models.FileField(upload_to='maintenance_documents/')
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_maintenance_documents')

    class Meta:
        db_table = 'maintenance_documents'
        ordering = ['-created_at']
        verbose_name = 'Maintenance Document'
        verbose_name_plural = 'Maintenance Documents'

    def __str__(self):
        return self.title
