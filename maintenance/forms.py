from django import forms
from .models import MaintenanceRequest, MaintenanceType
from assets.models import Vendor


class MaintenanceRequestForm(forms.ModelForm):
    """Form for creating ad-hoc maintenance requests"""
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'maintenance_type',
            'request_type',
            'priority',
            'issue_description',
            'impact_description',
            'vendor',
            'estimated_cost',
        ]
        widgets = {
            'issue_description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the maintenance issue...'
            }),
            'impact_description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Describe the impact on operations (optional)...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Filter maintenance types and vendors by company
        if company:
            self.fields['maintenance_type'].queryset = MaintenanceType.objects.filter(
                company=company, 
                is_deleted=False,
                is_active=True
            )
            self.fields['vendor'].queryset = Vendor.objects.filter(
                company=company,
                is_deleted=False,
                is_active=True,
                vendor_type='MAINTENANCE'
            )
        
        # Make vendor optional
        self.fields['vendor'].required = False
        self.fields['estimated_cost'].required = False
        self.fields['impact_description'].required = False
