from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Asset CRUD
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/create/', views.asset_create, name='asset_create'),
    path('assets/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('assets/<int:pk>/update/', views.asset_update, name='asset_update'),
    path('assets/<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    
    # QR Code & Scanning
    path('qr-scanner/', views.qr_scanner, name='qr_scanner'),
    path('assets/<int:pk>/qr-code/', views.asset_qr_code, name='asset_qr_code'),
    path('assets/qr/<uuid:qr_code>/', views.asset_detail_by_qr, name='asset_detail_by_qr'),
    
    # Documents
    path('assets/<int:pk>/add-document/', views.asset_add_document, name='asset_add_document'),
    
    # Financial Management
    path('financial/', views.financial_dashboard, name='financial_dashboard'),
    path('assets/<int:pk>/depreciation/', views.asset_depreciation, name='asset_depreciation'),
    
    # Asset Monitoring & Control
    path('monitoring/', views.monitoring_dashboard, name='monitoring_dashboard'),
    
    # Categories, Types, Vendors
    path('categories/', views.asset_categories, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('types/', views.asset_types, name='type_list'),
    path('types/create/', views.type_create, name='type_create'),
    path('types/<int:pk>/update/', views.type_update, name='type_update'),
    path('types/<int:pk>/delete/', views.type_delete, name='type_delete'),
    path('vendors/', views.vendors, name='vendor_list'),
    path('vendors/create/', views.vendor_create, name='vendor_create'),
    path('vendors/<int:pk>/update/', views.vendor_update, name='vendor_update'),
    path('vendors/<int:pk>/delete/', views.vendor_delete, name='vendor_delete'),
    
    # Audit Trail
    path('audit/', views.audit_trail, name='audit_trail'),
    path('audit/company-report/', views.company_audit_report, name='company_audit_report'),
    path('audit/asset/<int:pk>/', views.asset_audit_detail, name='asset_audit_detail'),
    path('audit/export/', views.audit_export, name='audit_export'),
    
    # Reports & Analytics
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/asset-summary/', views.report_asset_summary, name='report_asset_summary'),
    path('reports/asset-list/', views.report_asset_list, name='report_asset_list'),
    path('reports/financial/', views.report_financial, name='report_financial'),
    path('reports/maintenance/', views.report_maintenance, name='report_maintenance'),
    path('reports/transfer/', views.report_transfer, name='report_transfer'),
    path('reports/disposal/', views.report_disposal, name='report_disposal'),
    
    # API Endpoints
    path('api/asset-lookup/', views.asset_lookup_api, name='asset_lookup_api'),
    path('api/locations/', views.locations_api, name='locations_api'),
    path('api/record-movement/', views.record_asset_movement, name='record_movement_api'),
]
