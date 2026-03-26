from django import forms
from .models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'code', 'email', 'phone', 'website',
            'address_line1', 'address_line2', 'city', 'province', 'country', 'postal_code',
            'ipa_registration', 'tin', 'logo',
            'subscription_start_date', 'subscription_end_date',
            'max_users', 'max_assets',
            'is_active', 'notes',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'Company Name'}),
            'code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'COMP-001'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'contact@company.com'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': '+675 XXX XXXX'}),
            'website': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'https://company.com'}),
            'address_line1': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'Street Address Line 1'}),
            'address_line2': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'Street Address Line 2'}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'City'}),
            'province': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'Province'}),
            'country': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'Papua New Guinea'}),
            'postal_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'Postal Code'}),
            'ipa_registration': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'IPA Registration Number'}),
            'tin': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': 'TIN (optional)'}),
            'subscription_start_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'type': 'date'}),
            'subscription_end_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'type': 'date'}),
            'max_users': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': '25', 'min': '1', 'max': '25'}),
            'max_assets': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'placeholder': '1500', 'min': '1', 'max': '1500'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500', 'rows': 3, 'placeholder': 'Additional notes...'}),
            'logo': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded'}),
        }
