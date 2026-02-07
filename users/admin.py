# Django admin has been disabled - using custom forms only
# from django.contrib import admin
# from .models import Department, Location, UserProfile


# @admin.register(Department)
class DepartmentAdmin:
    list_display = ('code', 'name', 'head', 'parent_department', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    raw_id_fields = ('head', 'parent_department')
    list_per_page = 25


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'state', 'location_type', 'is_active', 'created_at')
    list_filter = ('location_type', 'is_active', 'state', 'created_at')
    search_fields = ('name', 'code', 'city', 'address_line1')
    list_per_page = 25


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'location', 'designation', 'is_asset_custodian', 'is_asset_approver')
    list_filter = ('is_asset_custodian', 'is_asset_approver', 'department', 'location', 'created_at')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name', 'designation')
    raw_id_fields = ('user', 'department', 'location', 'reporting_manager')
    list_per_page = 25
