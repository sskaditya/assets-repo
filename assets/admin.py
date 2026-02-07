# Django admin has been disabled - using custom forms only
# from django.contrib import admin
# from .models import AssetCategory, AssetType, Vendor, Asset, AssetDocument, AssetHistory, AssetTransfer, AssetDisposal


# @admin.register(AssetCategory)
class AssetCategoryAdmin:
    list_display = ('code', 'name', 'parent_category', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    raw_id_fields = ('parent_category',)
    list_per_page = 25


@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'category_type', 'requires_calibration', 'requires_insurance', 'is_active')
    list_filter = ('category_type', 'is_active', 'requires_calibration', 'requires_insurance', 'created_at')
    search_fields = ('name', 'code', 'description')
    raw_id_fields = ('category',)
    list_per_page = 25


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'vendor_type', 'contact_person', 'phone', 'email', 'is_active')
    list_filter = ('vendor_type', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'contact_person', 'email', 'gstin', 'pan')
    list_per_page = 25


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_tag', 'name', 'asset_type', 'status', 'location', 'department', 'assigned_to', 'created_at')
    list_filter = ('status', 'condition', 'asset_type', 'category', 'location', 'department', 'is_critical', 'is_insured', 'created_at')
    search_fields = ('asset_tag', 'name', 'serial_number', 'description', 'make', 'model')
    raw_id_fields = ('asset_type', 'category', 'location', 'department', 'assigned_to', 'custodian', 'vendor', 'amc_vendor')
    readonly_fields = ('qr_code', 'created_at', 'updated_at')
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('asset_tag', 'qr_code', 'qr_code_image', 'name', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'asset_type')
        }),
        ('Asset Details', {
            'fields': ('make', 'model', 'serial_number', 'specifications')
        }),
        ('Status', {
            'fields': ('status', 'condition')
        }),
        ('Location & Assignment', {
            'fields': ('location', 'department', 'assigned_to', 'custodian')
        }),
        ('Procurement', {
            'fields': ('vendor', 'purchase_order_number', 'purchase_date', 'purchase_price', 'invoice_number', 'invoice_date')
        }),
        ('Warranty', {
            'fields': ('warranty_start_date', 'warranty_end_date', 'warranty_period_months')
        }),
        ('AMC', {
            'fields': ('amc_vendor', 'amc_start_date', 'amc_end_date', 'amc_cost')
        }),
        ('Depreciation', {
            'fields': ('depreciation_rate', 'salvage_value', 'useful_life_years')
        }),
        ('Insurance', {
            'fields': ('is_insured', 'insurance_policy_number', 'insurance_expiry_date')
        }),
        ('Additional Information', {
            'fields': ('is_critical', 'notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(AssetDocument)
class AssetDocumentAdmin(admin.ModelAdmin):
    list_display = ('asset', 'document_type', 'title', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('title', 'description', 'asset__asset_tag')
    raw_id_fields = ('asset', 'uploaded_by')
    list_per_page = 25


@admin.register(AssetHistory)
class AssetHistoryAdmin(admin.ModelAdmin):
    list_display = ('asset', 'action_type', 'action_date', 'performed_by', 'from_location', 'to_location')
    list_filter = ('action_type', 'action_date')
    search_fields = ('asset__asset_tag', 'remarks')
    raw_id_fields = ('asset', 'performed_by', 'from_location', 'to_location', 'from_user', 'to_user')
    readonly_fields = ('action_date',)
    list_per_page = 25


@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_number', 'asset', 'status', 'from_location', 'to_location', 'requested_by', 'requested_date')
    list_filter = ('status', 'requested_date', 'approval_date')
    search_fields = ('transfer_number', 'asset__asset_tag', 'asset__name', 'reason')
    raw_id_fields = ('asset', 'from_user', 'to_user', 'from_location', 'to_location', 'from_department', 'to_department', 'requested_by', 'approved_by', 'completed_by')
    readonly_fields = ('transfer_number', 'requested_date')
    list_per_page = 25
    
    fieldsets = (
        ('Transfer Information', {
            'fields': ('transfer_number', 'asset', 'status')
        }),
        ('From', {
            'fields': ('from_user', 'from_location', 'from_department')
        }),
        ('To', {
            'fields': ('to_user', 'to_location', 'to_department')
        }),
        ('Request Details', {
            'fields': ('requested_by', 'requested_date', 'reason')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approval_date', 'approval_remarks')
        }),
        ('Completion', {
            'fields': ('completed_by', 'completed_date', 'transfer_document')
        }),
    )


@admin.register(AssetDisposal)
class AssetDisposalAdmin(admin.ModelAdmin):
    list_display = ('disposal_number', 'asset', 'status', 'disposal_method', 'disposal_value', 'requested_by', 'requested_date')
    list_filter = ('status', 'disposal_method', 'requested_date', 'approval_date')
    search_fields = ('disposal_number', 'asset__asset_tag', 'asset__name', 'reason')
    raw_id_fields = ('asset', 'requested_by', 'approved_by', 'completed_by')
    readonly_fields = ('disposal_number', 'requested_date')
    list_per_page = 25
    
    fieldsets = (
        ('Disposal Information', {
            'fields': ('disposal_number', 'asset', 'status', 'disposal_method')
        }),
        ('Financial Details', {
            'fields': ('current_book_value', 'disposal_value', 'disposal_cost')
        }),
        ('Request Details', {
            'fields': ('requested_by', 'requested_date', 'reason')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approval_date', 'approval_remarks')
        }),
        ('Completion', {
            'fields': ('completed_by', 'completed_date', 'buyer_details', 'disposal_document')
        }),
    )
