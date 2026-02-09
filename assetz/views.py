from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout


def landing(request):
    """Landing page for Softlogic AI Assetz"""
    return render(request, "landing.html")


def index(request):
    """Dashboard view"""
    return render(request, 'index.html')


def form_example(request):
    """Form example view"""
    if request.method == 'POST':
        # Handle form submission
        asset_name = request.POST.get('asset_name')
        asset_id = request.POST.get('asset_id')
        category = request.POST.get('category')
        value = request.POST.get('value')
        status = request.POST.get('status')
        description = request.POST.get('description')
        
        # Add your logic here (e.g., save to database)
        # For now, just render the form again
        return render(request, 'form_example.html', {
            'success': True,
            'message': 'Asset added successfully!'
        })
    
    return render(request, 'form_example.html')


def logout_view(request):
    """Custom logout view that accepts GET requests"""
    auth_logout(request)
    return redirect('landing')
