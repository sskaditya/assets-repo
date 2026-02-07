from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Company
from .forms import CompanyForm


@login_required
def company_list(request):
    """List all companies (Super Admin only)"""
    if not getattr(request, 'is_super_admin', False):
        messages.error(request, 'Only super admin can access company management')
        return redirect('assets:dashboard')
    
    companies = Company.objects.filter(is_deleted=False).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(companies, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'core/company_list.html', context)


@login_required
def company_create(request):
    """Create new company (Super Admin only)"""
    if not getattr(request, 'is_super_admin', False):
        messages.error(request, 'Only super admin can create companies')
        return redirect('assets:dashboard')
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save()
            messages.success(request, f'Company "{company.name}" created successfully!')
            return redirect('core:company_list')
    else:
        form = CompanyForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    
    return render(request, 'core/company_form.html', context)


@login_required
def company_detail(request, pk):
    """View company details (Super Admin only)"""
    if not getattr(request, 'is_super_admin', False):
        messages.error(request, 'Only super admin can view company details')
        return redirect('assets:dashboard')
    
    company = get_object_or_404(Company, pk=pk, is_deleted=False)
    
    # Get company statistics
    from assets.models import Asset
    from users.models import UserProfile
    
    stats = {
        'total_assets': Asset.objects.filter(company=company, is_deleted=False).count(),
        'total_users': UserProfile.objects.filter(company=company).count(),
        'active_assets': Asset.objects.filter(company=company, status='IN_USE', is_deleted=False).count(),
    }
    
    context = {
        'company': company,
        'stats': stats,
    }
    
    return render(request, 'core/company_detail.html', context)


@login_required
def company_update(request, pk):
    """Update company (Super Admin only)"""
    if not getattr(request, 'is_super_admin', False):
        messages.error(request, 'Only super admin can update companies')
        return redirect('assets:dashboard')
    
    company = get_object_or_404(Company, pk=pk, is_deleted=False)
    
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            company = form.save()
            messages.success(request, f'Company "{company.name}" updated successfully!')
            return redirect('core:company_detail', pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    
    context = {
        'form': form,
        'company': company,
        'action': 'Update',
    }
    
    return render(request, 'core/company_form.html', context)


@login_required
def company_delete(request, pk):
    """Delete company (Super Admin only)"""
    if not getattr(request, 'is_super_admin', False):
        messages.error(request, 'Only super admin can delete companies')
        return redirect('assets:dashboard')
    
    company = get_object_or_404(Company, pk=pk, is_deleted=False)
    
    if request.method == 'POST':
        company.is_deleted = True
        company.save()
        messages.success(request, f'Company "{company.name}" deleted successfully!')
        return redirect('core:company_list')
    
    context = {
        'company': company,
    }
    
    return render(request, 'core/company_confirm_delete.html', context)
