from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel, Company


class Department(BaseModel):
    """Department model for organizing users and assets"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    parent_department = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_departments')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'departments'
        ordering = ['company', 'name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        unique_together = [['company', 'code'], ['company', 'name']]

    def __str__(self):
        if self.company:
            return f"{self.company.code} - {self.code} - {self.name}"
        return f"{self.code} - {self.name}"


class Location(BaseModel):
    """Location model for tracking asset locations"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    postal_code = models.CharField(max_length=20)
    location_type = models.CharField(max_length=50, choices=[
        ('OFFICE', 'Office'),
        ('WAREHOUSE', 'Warehouse'),
        ('FACTORY', 'Factory'),
        ('BRANCH', 'Branch'),
        ('DATA_CENTER', 'Data Center'),
        ('OTHER', 'Other'),
    ], default='OFFICE')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'locations'
        ordering = ['company', 'name']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        unique_together = [['company', 'code'], ['company', 'name']]

    def __str__(self):
        if self.company:
            return f"{self.company.code} - {self.code} - {self.name}"
        return f"{self.code} - {self.name}"


class UserProfile(BaseModel):
    """Extended user profile for additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='user_profiles')
    employee_id = models.CharField(max_length=50, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    designation = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    reporting_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members')
    is_asset_custodian = models.BooleanField(default=False, help_text="Can this user be assigned as asset custodian?")
    is_asset_approver = models.BooleanField(default=False, help_text="Can this user approve asset requests?")
    is_company_admin = models.BooleanField(default=False, help_text="Is this user a company admin?")

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        unique_together = [['company', 'employee_id']]

    def __str__(self):
        parts = []
        if self.company:
            parts.append(self.company.code)
        if self.user:
            parts.append(self.user.get_full_name())
            if self.employee_id:
                parts[-1] = f"{parts[-1]} ({self.employee_id})"
        return " - ".join(parts) if parts else "User Profile"
