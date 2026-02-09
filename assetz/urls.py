"""
URL configuration for assetz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Django admin has been removed - using custom forms only
    path("", views.landing, name="landing"),  # Landing page
    path("app/", include('assets.urls')),  # Asset management app
    path("core/", include('core.urls')),  # Core app (companies)
    path("users/", include('users.urls')),  # User management
    
    # Custom authentication URLs
    path("accounts/login/", auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("accounts/logout/", views.logout_view, name='logout'),
    path("accounts/password_reset/", auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path("accounts/password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path("accounts/reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path("accounts/reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    # Legacy routes
    path("home/", views.index, name="index"),
    path("form-example/", views.form_example, name="form_example"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
