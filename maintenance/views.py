from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from assets.models import Asset
from .forms import MaintenanceRequestForm
from .models import MaintenanceRequest
from datetime import datetime


@login_required
def maintenance_request_create(request, asset_id):
    """Create a new maintenance request for an asset"""
    asset = get_object_or_404(Asset, pk=asset_id, is_deleted=False)
    company = getattr(request, 'current_company', None)
    
    # Ensure user has access to this asset's company
    if company and asset.company != company:
        messages.error(request, 'You do not have permission to request maintenance for this asset.')
        return redirect('assets:asset_detail', pk=asset_id)
    
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, company=company)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.asset = asset
            maintenance_request.company = company or asset.company
            maintenance_request.requested_by = request.user
            
            # Generate request number
            today = datetime.now()
            prefix = f"MR-{today.strftime('%Y%m')}"
            last_request = MaintenanceRequest.objects.filter(
                request_number__startswith=prefix
            ).order_by('-request_number').first()
            
            if last_request:
                last_number = int(last_request.request_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            maintenance_request.request_number = f"{prefix}-{new_number:04d}"
            maintenance_request.save()
            
            messages.success(
                request, 
                f'Maintenance request {maintenance_request.request_number} created successfully!'
            )
            return redirect('assets:asset_detail', pk=asset_id)
    else:
        form = MaintenanceRequestForm(company=company)
    
    context = {
        'form': form,
        'asset': asset,
        'title': 'Request Maintenance',
    }
    
    return render(request, 'maintenance/maintenance_request_form.html', context)
