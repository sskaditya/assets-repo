from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import UserProfile, Department, Location
from .forms import UserCreateForm, UserUpdateForm, UserProfileUpdateForm
from core.models import Company
from core.audit_utils import log_create, log_update, log_delete


def is_super_admin(user):
    """Check if user is super admin"""
    return user.is_superuser


def is_company_admin_check(user):
    """Check if user is company admin or super admin"""
    if user.is_superuser:
        return True
    try:
        return user.profile.is_company_admin
    except:
        return False


@login_required
@user_passes_test(is_company_admin_check)
def user_list(request):
    """List all users"""
    company = getattr(request, 'current_company', None)
    is_super_admin = getattr(request, 'is_super_admin', False)
    
    # Base queryset
    if company:
        # Company admin sees only their company's users
        users = User.objects.filter(profile__company=company).select_related('profile', 'profile__company', 'profile__department', 'profile__location')
    elif is_super_admin:
        # Super admin sees all users
        users = User.objects.all().select_related('profile', 'profile__company', 'profile__department', 'profile__location')
    else:
        # Regular user shouldn't access this
        messages.error(request, 'You do not have permission to access user management.')
        return redirect('assets:dashboard')
    
    # Search filter
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(profile__employee_id__icontains=search)
        )
    
    # Status filter
    status = request.GET.get('status', '')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    # Company filter (for super admin only)
    company_filter = request.GET.get('company', '')
    if company_filter and is_super_admin:
        users = users.filter(profile__company_id=company_filter)
    
    users = users.order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(users, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get companies for filter (super admin only)
    companies = None
    if is_super_admin:
        companies = Company.objects.filter(is_deleted=False, is_active=True)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'company': company,
        'is_super_admin': is_super_admin,
        'companies': companies,
        'company_filter': company_filter,
    }
    
    return render(request, 'users/user_list.html', context)


@login_required
@user_passes_test(is_company_admin_check)
def user_create(request):
    """Create a new user"""
    company = getattr(request, 'current_company', None)
    is_super_admin = getattr(request, 'is_super_admin', False)
    
    if request.method == 'POST':
        form = UserCreateForm(request.POST, company=company if not is_super_admin else None)
        if form.is_valid():
            user = form.save()
            # Log the user creation
            log_create(request, user.profile, metadata={'created_by_admin': True})
            messages.success(request, f'User "{user.get_full_name()}" created successfully!')
            return redirect('users:user_list')
    else:
        form = UserCreateForm(company=company if not is_super_admin else None)
    
    context = {
        'form': form,
        'title': 'Create User',
        'company': company,
        'is_super_admin': is_super_admin,
    }
    
    return render(request, 'users/user_form.html', context)


@login_required
@user_passes_test(is_company_admin_check)
def user_detail(request, pk):
    """View user details"""
    user = get_object_or_404(User, pk=pk)
    company = getattr(request, 'current_company', None)
    is_super_admin = getattr(request, 'is_super_admin', False)
    
    # Check permission
    if not is_super_admin and company:
        try:
            if user.profile.company != company:
                messages.error(request, 'You do not have permission to view this user.')
                return redirect('users:user_list')
        except:
            pass
    
    # Get user's assets
    try:
        profile = user.profile
        assigned_assets = user.assigned_assets.filter(is_deleted=False)[:10]
        custodian_assets = user.custodian_assets.filter(is_deleted=False)[:10]
    except:
        profile = None
        assigned_assets = []
        custodian_assets = []
    
    context = {
        'user_obj': user,
        'profile': profile,
        'assigned_assets': assigned_assets,
        'custodian_assets': custodian_assets,
        'company': company,
        'is_super_admin': is_super_admin,
    }
    
    return render(request, 'users/user_detail.html', context)


@login_required
@user_passes_test(is_company_admin_check)
def user_update(request, pk):
    """Update user information"""
    user = get_object_or_404(User, pk=pk)
    company = getattr(request, 'current_company', None)
    is_super_admin = getattr(request, 'is_super_admin', False)
    
    # Check permission
    if not is_super_admin and company:
        try:
            if user.profile.company != company:
                messages.error(request, 'You do not have permission to edit this user.')
                return redirect('users:user_list')
        except:
            pass
    
    try:
        profile = user.profile
    except:
        # Create profile if it doesn't exist
        if company or is_super_admin:
            profile = UserProfile.objects.create(
                user=user,
                company=company or Company.objects.first()
            )
        else:
            messages.error(request, 'User profile not found.')
            return redirect('users:user_list')
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileUpdateForm(request.POST, instance=profile, company=profile.company)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Store old instance for audit logging
            old_profile = UserProfile.objects.get(pk=profile.pk)
            
            user_form.save()
            profile_form.save()
            
            # Log the update
            log_update(request, profile, old_profile, metadata={'updated_by_admin': True})
            
            messages.success(request, f'User "{user.get_full_name()}" updated successfully!')
            return redirect('users:user_detail', pk=user.pk)
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileUpdateForm(instance=profile, company=profile.company)
    
    context = {
        'user_obj': user,
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Update User',
        'company': company,
        'is_super_admin': is_super_admin,
    }
    
    return render(request, 'users/user_update.html', context)


@login_required
@user_passes_test(is_company_admin_check)
def user_delete(request, pk):
    """Delete/deactivate user"""
    user = get_object_or_404(User, pk=pk)
    company = getattr(request, 'current_company', None)
    is_super_admin = getattr(request, 'is_super_admin', False)
    
    # Check permission
    if not is_super_admin and company:
        try:
            if user.profile.company != company:
                messages.error(request, 'You do not have permission to delete this user.')
                return redirect('users:user_list')
        except:
            pass
    
    # Prevent self-deletion
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('users:user_list')
    
    if request.method == 'POST':
        # Log before deactivating
        log_delete(request, user.profile, metadata={
            'action': 'deactivate',
            'reason': 'User deactivated by admin',
            'deactivated_by': request.user.username
        })
        
        user.is_active = False
        user.save()
        messages.success(request, f'User "{user.get_full_name()}" has been deactivated.')
        return redirect('users:user_list')
    
    context = {
        'user_obj': user,
        'company': company,
        'is_super_admin': is_super_admin,
    }
    
    return render(request, 'users/user_confirm_delete.html', context)


@login_required
@user_passes_test(is_super_admin)
def department_list(request):
    """List all departments"""
    company = getattr(request, 'current_company', None)
    is_super_admin = getattr(request, 'is_super_admin', False)
    
    if company:
        departments = Department.objects.filter(company=company, is_deleted=False).annotate(
            employee_count=Count('employees')
        ).order_by('name')
    else:
        departments = Department.objects.filter(is_deleted=False).select_related('company').annotate(
            employee_count=Count('employees')
        ).order_by('company__name', 'name')
    
    context = {
        'departments': departments,
        'company': company,
        'is_super_admin': is_super_admin,
    }
    
    return render(request, 'users/department_list.html', context)


@login_required
@user_passes_test(is_super_admin)
def location_list(request):
    """List all locations"""
    company = getattr(request, 'current_company', None)
    is_super_admin = getattr(request, 'is_super_admin', False)
    
    if company:
        locations = Location.objects.filter(company=company, is_deleted=False).annotate(
            employee_count=Count('employees'),
            asset_count=Count('assets', filter=Q(assets__is_deleted=False))
        ).order_by('name')
    else:
        locations = Location.objects.filter(is_deleted=False).select_related('company').annotate(
            employee_count=Count('employees'),
            asset_count=Count('assets', filter=Q(assets__is_deleted=False))
        ).order_by('company__name', 'name')
    
    context = {
        'locations': locations,
        'company': company,
        'is_super_admin': is_super_admin,
    }
    
    return render(request, 'users/location_list.html', context)


@login_required
@user_passes_test(is_company_admin_check)
def department_create(request):
    """Create a new department"""
    from .forms import DepartmentForm
    from core.audit_utils import log_create
    
    company = getattr(request, 'current_company', None)
    is_super_admin = getattr(request, 'is_super_admin', False)
    
    # For non-super admins, company context is required
    if not is_super_admin and not company:
        messages.error(request, 'Company context is required to create a department')
        return redirect('users:department_list')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, company=company, is_super_admin=is_super_admin)
        if form.is_valid():
            department = form.save(commit=False)
            
            # For super admin, get company from form; for company admin, use context
            if is_super_admin and not company:
                department.company = form.cleaned_data.get('company')
            else:
                department.company = company
            
            department.save()
            
            # Log the creation
            log_create(request, department, metadata={
                'action': 'department_created',
                'department_name': department.name,
                'department_code': department.code,
                'company': department.company.name if department.company else 'N/A'
            })
            
            messages.success(request, f'Department "{department.name}" has been created successfully.')
            return redirect('users:department_list')
    else:
        form = DepartmentForm(company=company, is_super_admin=is_super_admin)
    
    context = {
        'form': form,
        'company': company,
        'is_super_admin': is_super_admin,
        'title': 'Create Department',
    }
    
    return render(request, 'users/department_form.html', context)


@login_required
@user_passes_test(is_company_admin_check)
def location_create(request):
    """Create a new location"""
    from .forms import LocationForm
    from core.audit_utils import log_create
    
    company = getattr(request, 'current_company', None)
    is_super_admin = getattr(request, 'is_super_admin', False)
    
    # For non-super admins, company context is required
    if not is_super_admin and not company:
        messages.error(request, 'Company context is required to create a location')
        return redirect('users:location_list')
    
    if request.method == 'POST':
        form = LocationForm(request.POST, company=company, is_super_admin=is_super_admin)
        if form.is_valid():
            location = form.save(commit=False)
            
            # For super admin, get company from form; for company admin, use context
            if is_super_admin and not company:
                location.company = form.cleaned_data.get('company')
            else:
                location.company = company
            
            location.save()
            
            # Log the creation
            log_create(request, location, metadata={
                'action': 'location_created',
                'location_name': location.name,
                'location_code': location.code,
                'company': location.company.name if location.company else 'N/A'
            })
            
            messages.success(request, f'Location "{location.name}" has been created successfully.')
            return redirect('users:location_list')
    else:
        form = LocationForm(company=company, is_super_admin=is_super_admin)
    
    context = {
        'form': form,
        'company': company,
        'is_super_admin': is_super_admin,
        'title': 'Create Location',
    }
    
    return render(request, 'users/location_form.html', context)
