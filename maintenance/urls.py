from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('request/<int:asset_id>/', views.maintenance_request_create, name='request_create'),
]
