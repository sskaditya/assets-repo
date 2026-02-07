# Django admin has been disabled - using custom forms only
# from django.contrib import admin
# from .models import MaintenanceType, MaintenanceSchedule, MaintenanceRequest, MaintenanceLog, MaintenanceDocument


# @admin.register(MaintenanceType)
class MaintenanceTypeAdmin:
    list_display = ('code', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    list_per_page = 25


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ('asset', 'maintenance_type', 'frequency', 'next_due_date', 'last_completed_date', 'is_active')
    list_filter = ('frequency', 'is_active', 'next_due_date', 'created_at')
    search_fields = ('asset__asset_tag', 'asset__name', 'notes')
    raw_id_fields = ('asset', 'maintenance_type', 'assigned_to', 'vendor')
    date_hierarchy = 'next_due_date'
    list_per_page = 25


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'asset', 'request_type', 'priority', 'status', 'requested_by', 'requested_date')
    list_filter = ('request_type', 'priority', 'status', 'requested_date', 'scheduled_date')
    search_fields = ('request_number', 'asset__asset_tag', 'asset__name', 'issue_description')
    raw_id_fields = ('asset', 'maintenance_type', 'requested_by', 'approved_by', 'assigned_to', 'vendor')
    readonly_fields = ('request_number', 'requested_date')
    date_hierarchy = 'requested_date'
    list_per_page = 25
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_number', 'asset', 'maintenance_type', 'request_type', 'priority', 'status')
        }),
        ('Request Details', {
            'fields': ('issue_description', 'impact_description', 'requested_by', 'requested_date')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_date', 'rejection_reason')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'vendor', 'scheduled_date')
        }),
        ('Execution', {
            'fields': ('started_date', 'completed_date', 'resolution_notes', 'downtime_hours')
        }),
        ('Cost', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
    )


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('asset', 'maintenance_type', 'maintenance_date', 'performed_by', 'total_cost', 'duration_hours')
    list_filter = ('maintenance_date', 'maintenance_type', 'created_at')
    search_fields = ('asset__asset_tag', 'asset__name', 'work_description', 'parts_replaced')
    raw_id_fields = ('maintenance_request', 'asset', 'maintenance_type', 'performed_by', 'vendor')
    date_hierarchy = 'maintenance_date'
    list_per_page = 25


@admin.register(MaintenanceDocument)
class MaintenanceDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'maintenance_request', 'maintenance_log', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('title', 'description')
    raw_id_fields = ('maintenance_request', 'maintenance_log', 'uploaded_by')
    list_per_page = 25
