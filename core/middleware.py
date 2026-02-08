"""
Middleware for multi-company/multi-tenancy support
"""
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse


class CompanyMiddleware(MiddlewareMixin):
    """
    Middleware to set the current company context based on the logged-in user.
    This enables automatic filtering of data by company.
    """
    
    def process_request(self, request):
        # Skip for login, logout, landing page, and static files
        if (request.path.startswith('/accounts/') or 
            request.path.startswith('/static/') or 
            request.path.startswith('/media/') or
            request.path == '/'):  # Landing page
            return None
        
        # Set company context
        if request.user.is_authenticated:
            # Check if user is superuser (Softlogic super admin)
            if request.user.is_superuser:
                request.is_super_admin = True
                # Super admin can optionally select a company to view
                selected_company_id = request.session.get('selected_company_id')
                if selected_company_id:
                    try:
                        from .models import Company
                        request.current_company = Company.objects.get(id=selected_company_id, is_deleted=False)
                    except:
                        request.current_company = None
                else:
                    request.current_company = None
                return None
            
            # Get user profile to determine company
            try:
                profile = request.user.profile
                request.current_company = profile.company
                request.is_super_admin = False
                request.is_company_admin = profile.is_company_admin
            except:
                # User has no profile - redirect to dashboard with error message
                # The user should contact an administrator to set up their profile
                from django.contrib import messages
                messages.error(request, 'Your profile is not set up. Please contact your administrator.')
                if request.path != reverse('assets:dashboard'):
                    return redirect(reverse('assets:dashboard'))
        else:
            request.current_company = None
            request.is_super_admin = False
            request.is_company_admin = False
        
        return None


def get_current_company(request):
    """
    Helper function to get the current company from request.
    Returns None if super admin or no company context.
    """
    return getattr(request, 'current_company', None)


def is_super_admin(request):
    """
    Helper function to check if the current user is a super admin.
    """
    return getattr(request, 'is_super_admin', False)


def is_company_admin(request):
    """
    Helper function to check if the current user is a company admin.
    """
    return getattr(request, 'is_company_admin', False)
