# Django admin has been disabled - using custom forms only
# from django.contrib import admin
# from .models import Company


# @admin.register(Company)
class CompanyAdmin:
    list_display = ('code', 'name', 'email', 'phone', 'city', 'is_active', 'is_subscription_active', 'created_at')
    list_filter = ('is_active', 'country', 'created_at')
    search_fields = ('name', 'code', 'email', 'tax_id', 'gstin')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'logo', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code')
        }),
        ('Tax Information', {
            'fields': ('tax_id', 'gstin')
        }),
        ('Subscription', {
            'fields': ('subscription_start_date', 'subscription_end_date', 'max_users', 'max_assets')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
    
    def is_subscription_active(self, obj):
        return obj.is_subscription_active
    is_subscription_active.boolean = True
    is_subscription_active.short_description = 'Subscription Active'
