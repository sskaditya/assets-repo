from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Department, Location
from core.models import Company
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class UserCreateForm(UserCreationForm):
    """Form for creating a new user with profile"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Profile fields
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_deleted=False, is_active=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    employee_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'EMP-001'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.filter(is_deleted=False, is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_deleted=False, is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    designation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Asset Manager'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'})
    )
    mobile = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'})
    )
    is_asset_custodian = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_asset_approver = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_company_admin = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Filter department and location by company if provided
        if company:
            self.fields['department'].queryset = Department.objects.filter(
                company=company, is_deleted=False, is_active=True
            )
            self.fields['location'].queryset = Location.objects.filter(
                company=company, is_deleted=False, is_active=True
            )
            self.fields['company'].initial = company
            self.fields['company'].widget = forms.HiddenInput()
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = self.cleaned_data.get('is_active', True)
        
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                company=self.cleaned_data['company'],
                employee_id=self.cleaned_data.get('employee_id'),
                department=self.cleaned_data.get('department'),
                location=self.cleaned_data.get('location'),
                designation=self.cleaned_data.get('designation'),
                phone=self.cleaned_data.get('phone'),
                mobile=self.cleaned_data.get('mobile'),
                is_asset_custodian=self.cleaned_data.get('is_asset_custodian', False),
                is_asset_approver=self.cleaned_data.get('is_asset_approver', False),
                is_company_admin=self.cleaned_data.get('is_company_admin', False),
            )
        
        return user


class UserUpdateForm(forms.ModelForm):
    """Form for updating user information"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'is_active']


class UserProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = UserProfile
        fields = [
            'employee_id', 'department', 'location', 'designation',
            'phone', 'mobile', 'reporting_manager',
            'is_asset_custodian', 'is_asset_approver', 'is_company_admin'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'reporting_manager': forms.Select(attrs={'class': 'form-select'}),
            'is_asset_custodian': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_asset_approver': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_company_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        
        # Filter department and location by company
        if company:
            self.fields['department'].queryset = Department.objects.filter(
                company=company, is_deleted=False, is_active=True
            )
            self.fields['location'].queryset = Location.objects.filter(
                company=company, is_deleted=False, is_active=True
            )
            self.fields['reporting_manager'].queryset = User.objects.filter(
                profile__company=company, is_active=True
            )
        else:
            self.fields['department'].queryset = Department.objects.filter(
                is_deleted=False, is_active=True
            )
            self.fields['location'].queryset = Location.objects.filter(
                is_deleted=False, is_active=True
            )


class DepartmentForm(forms.ModelForm):
    """Form for creating and updating departments"""
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_deleted=False, is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Select company (for super admin only)'
    )
    
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'parent_department', 'head', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DEPT-001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Department description...'}),
            'parent_department': forms.Select(attrs={'class': 'form-select'}),
            'head': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        is_super_admin = kwargs.pop('is_super_admin', False)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        
        # For super admin, show company field; for company admin, hide it
        if is_super_admin and not company:
            self.fields['company'].required = True
            # Filter parent departments and heads - will be filtered by JS on company selection
            self.fields['parent_department'].queryset = Department.objects.filter(
                is_deleted=False, is_active=True
            )
            self.fields['head'].queryset = User.objects.filter(is_active=True)
        else:
            # Remove company field for company admins
            self.fields.pop('company', None)
            
            # Filter by company
            if company:
                self.fields['parent_department'].queryset = Department.objects.filter(
                    company=company, is_deleted=False, is_active=True
                )
                self.fields['head'].queryset = User.objects.filter(
                    profile__company=company, is_active=True
                )
            else:
                self.fields['parent_department'].queryset = Department.objects.filter(
                    is_deleted=False, is_active=True
                )
                self.fields['head'].queryset = User.objects.filter(is_active=True)


class LocationForm(forms.ModelForm):
    """Form for creating and updating locations"""
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_deleted=False, is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Select company (for super admin only)'
    )
    
    class Meta:
        model = Location
        fields = [
            'name', 'code', 'address_line1', 'address_line2', 
            'city', 'state', 'country', 'postal_code', 
            'location_type', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location Name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'LOC-001'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'location_type': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        is_super_admin = kwargs.pop('is_super_admin', False)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        
        # For super admin without company context, show company field
        if is_super_admin and not company:
            self.fields['company'].required = True
        else:
            # Remove company field for company admins
            self.fields.pop('company', None)
