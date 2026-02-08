from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Company Management
    path('companies/', views.company_list, name='company_list'),
    path('companies/create/', views.company_create, name='company_create'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('companies/<int:pk>/update/', views.company_update, name='company_update'),
    path('companies/<int:pk>/delete/', views.company_delete, name='company_delete'),
    path('set-company/<int:company_id>/', views.set_company_context, name='set_company_context'),
    path('clear-company/', views.set_company_context, name='clear_company_context'),
    
    # Audit Logs
    path('audit/', views.audit_log_list, name='audit_log_list'),
    path('audit/<int:pk>/', views.audit_log_detail, name='audit_log_detail'),
    path('audit/export/', views.audit_log_export, name='audit_log_export'),
    path('audit/activity/', views.user_activity_report, name='user_activity_report'),
    path('audit/activity/export/', views.user_activity_export, name='user_activity_export'),
]
