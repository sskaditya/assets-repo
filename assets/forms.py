from django import forms
from .models import Asset, AssetCategory, AssetType, Vendor, AssetDocument
from users.models import Department, Location
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field
from django.contrib.auth.models import User


class AssetFilterForm(forms.Form):
    """Form for filtering assets"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search by asset tag, name, serial number...', 'class': 'form-control'})
    )
    category = forms.ModelChoiceField(
        queryset=AssetCategory.objects.filter(is_active=True, is_deleted=False),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    asset_type = forms.ModelChoiceField(
        queryset=AssetType.objects.filter(is_active=True, is_deleted=False),
        required=False,
        empty_label="All Types",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Asset.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True, is_deleted=False),
        required=False,
        empty_label="All Locations",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_active=True, is_deleted=False),
        required=False,
        empty_label="All Departments",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class AssetForm(forms.ModelForm):
    """Form for creating and updating assets"""
    
    class Meta:
        model = Asset
        fields = [
            'asset_tag', 'name', 'description', 'category', 'asset_type',
            'make', 'model', 'serial_number', 'specifications',
            'status', 'condition', 'location', 'department',
            'assigned_to', 'custodian', 'vendor',
            'purchase_order_number', 'purchase_date', 'purchase_price',
            'invoice_number', 'invoice_date',
            'warranty_start_date', 'warranty_end_date', 'warranty_period_months',
            'amc_vendor', 'amc_start_date', 'amc_end_date', 'amc_cost',
            'depreciation_rate', 'salvage_value', 'useful_life_years',
            'is_critical', 'is_insured', 'insurance_policy_number',
            'insurance_expiry_date', 'notes'
        ]
        widgets = {
            'asset_tag': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'asset_type': forms.Select(attrs={'class': 'form-select'}),
            'make': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'custodian': forms.Select(attrs={'class': 'form-select'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'purchase_order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_period_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'amc_vendor': forms.Select(attrs={'class': 'form-select'}),
            'amc_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amc_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amc_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'depreciation_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'salvage_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'useful_life_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_critical': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_insured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'insurance_policy_number': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'


class AssetDocumentForm(forms.ModelForm):
    """Form for uploading asset documents"""
    
    class Meta:
        model = AssetDocument
        fields = ['document_type', 'title', 'document_file', 'description']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AssetCategoryForm(forms.ModelForm):
    """Form for creating and updating asset categories"""
    
    class Meta:
        model = AssetCategory
        fields = ['code', 'name', 'description', 'parent_category', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CAT-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Category description...'}),
            'parent_category': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        
        # Filter parent category by company if provided
        if company:
            self.fields['parent_category'].queryset = AssetCategory.objects.filter(
                company=company, is_deleted=False, is_active=True
            )


class AssetTypeForm(forms.ModelForm):
    """Form for creating and updating asset types"""
    
    class Meta:
        model = AssetType
        fields = [
            'code', 'name', 'description', 'category',
            'requires_calibration', 'requires_insurance', 'is_active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TYPE-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type description...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'requires_calibration': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_insurance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        
        # Filter category by company if provided
        if company:
            self.fields['category'].queryset = AssetCategory.objects.filter(
                company=company, is_deleted=False, is_active=True
            )


class VendorForm(forms.ModelForm):
    """Form for creating and updating vendors"""
    
    class Meta:
        model = Vendor
        fields = [
            'code', 'name', 'vendor_type', 'contact_person', 'phone', 'email',
            'address', 'city', 'state', 'country', 'postal_code',
            'gstin', 'pan', 'is_active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VND-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor Name'}),
            'vendor_type': forms.Select(attrs={'class': 'form-select'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'vendor@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Complete address...'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'gstin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GSTIN'}),
            'pan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAN'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
