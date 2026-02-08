"""
Audit Logging Utilities
Helper functions for logging user actions and tracking changes
"""
from django.contrib.contenttypes.models import ContentType
from django.db import models
from .models import AuditLog
import json


def get_client_ip(request):
    """Get the client's IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_model_fields(instance):
    """
    Get all field values of a model instance as a dictionary.
    Excludes certain fields and handles related objects.
    """
    data = {}
    exclude_fields = ['password', 'created_at', 'updated_at']
    
    for field in instance._meta.fields:
        if field.name in exclude_fields:
            continue
            
        value = getattr(instance, field.name)
        
        # Handle foreign keys
        if isinstance(field, models.ForeignKey) and value:
            data[field.name] = str(value)
            data[f'{field.name}_id'] = value.pk
        # Handle date/datetime
        elif hasattr(value, 'isoformat'):
            data[field.name] = value.isoformat()
        # Handle other values
        elif value is not None:
            try:
                json.dumps(value)  # Test if JSON serializable
                data[field.name] = value
            except (TypeError, ValueError):
                data[field.name] = str(value)
    
    return data


def log_action(request, instance, action, description=None, old_values=None, new_values=None, metadata=None):
    """
    Log an action to the audit trail.
    
    Args:
        request: Django request object
        instance: Model instance that was affected
        action: Action type ('CREATE', 'UPDATE', 'DELETE', etc.)
        description: Human-readable description (optional, will be auto-generated)
        old_values: Dictionary of old values (for UPDATE/DELETE)
        new_values: Dictionary of new values (for CREATE/UPDATE)
        metadata: Additional metadata dictionary
    
    Returns:
        AuditLog instance
    """
    if not request or not instance:
        return None
    
    # Get user info
    user = request.user if request.user.is_authenticated else None
    username = user.username if user else 'Anonymous'
    
    # Get content type
    content_type = ContentType.objects.get_for_model(instance)
    
    # Auto-generate description if not provided
    if not description:
        model_name = content_type.model
        if action == 'CREATE':
            description = f"Created {model_name}: {str(instance)}"
        elif action == 'UPDATE':
            description = f"Updated {model_name}: {str(instance)}"
        elif action == 'DELETE':
            description = f"Deleted {model_name}: {str(instance)}"
        else:
            description = f"{action} {model_name}: {str(instance)}"
    
    # Get request metadata
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    request_path = request.path
    request_method = request.method
    
    # Get company context
    company = getattr(request, 'current_company', None)
    
    # Create audit log
    audit_log = AuditLog.objects.create(
        user=user,
        username=username,
        content_type=content_type,
        object_id=str(instance.pk),
        object_repr=str(instance)[:500],
        action=action,
        description=description,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        user_agent=user_agent,
        request_path=request_path,
        request_method=request_method,
        company=company,
        metadata=metadata
    )
    
    return audit_log


def log_create(request, instance, metadata=None):
    """Log a CREATE action"""
    new_values = get_model_fields(instance)
    return log_action(
        request=request,
        instance=instance,
        action='CREATE',
        new_values=new_values,
        metadata=metadata
    )


def log_update(request, instance, old_instance=None, changed_fields=None, metadata=None):
    """
    Log an UPDATE action.
    
    Args:
        request: Django request object
        instance: Updated model instance
        old_instance: Previous version of the instance (optional)
        changed_fields: List of changed field names (optional)
        metadata: Additional metadata
    """
    new_values = get_model_fields(instance)
    old_values = get_model_fields(old_instance) if old_instance else None
    
    # Calculate changed fields if not provided
    if old_values and not changed_fields:
        changed_fields = []
        for key in new_values:
            if key in old_values and new_values[key] != old_values[key]:
                changed_fields.append(key)
    
    audit_log = log_action(
        request=request,
        instance=instance,
        action='UPDATE',
        old_values=old_values,
        new_values=new_values,
        metadata=metadata
    )
    
    if audit_log and changed_fields:
        audit_log.changed_fields = changed_fields
        audit_log.save(update_fields=['changed_fields'])
    
    return audit_log


def log_delete(request, instance, metadata=None):
    """Log a DELETE action"""
    old_values = get_model_fields(instance)
    return log_action(
        request=request,
        instance=instance,
        action='DELETE',
        old_values=old_values,
        metadata=metadata
    )


def log_view(request, instance, metadata=None):
    """Log a VIEW action (for sensitive data)"""
    return log_action(
        request=request,
        instance=instance,
        action='VIEW',
        description=f"Viewed {instance._meta.model_name}: {str(instance)}",
        metadata=metadata
    )


def log_export(request, model_name, count, format='Excel', metadata=None):
    """
    Log an EXPORT action.
    
    Args:
        request: Django request object
        model_name: Name of the model being exported
        count: Number of records exported
        format: Export format (Excel, CSV, PDF, etc.)
        metadata: Additional metadata
    """
    if not metadata:
        metadata = {}
    
    metadata.update({
        'model': model_name,
        'record_count': count,
        'format': format
    })
    
    # Create a dummy object for content type
    from django.apps import apps
    try:
        model_class = apps.get_model('core', model_name)
        content_type = ContentType.objects.get_for_model(model_class)
    except:
        content_type = None
    
    user = request.user if request.user.is_authenticated else None
    username = user.username if user else 'Anonymous'
    company = getattr(request, 'current_company', None)
    
    audit_log = AuditLog.objects.create(
        user=user,
        username=username,
        content_type=content_type,
        object_repr=f"{model_name} Export",
        action='EXPORT',
        description=f"Exported {count} {model_name} records to {format}",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        request_path=request.path,
        request_method=request.method,
        company=company,
        metadata=metadata
    )
    
    return audit_log


def log_login(request, user):
    """Log a LOGIN action"""
    if not user or not request:
        return None
    
    company = getattr(request, 'current_company', None)
    
    audit_log = AuditLog.objects.create(
        user=user,
        username=user.username,
        object_repr=f"User: {user.username}",
        action='LOGIN',
        description=f"User {user.username} logged in",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        request_path=request.path,
        request_method=request.method,
        company=company
    )
    
    return audit_log


def log_logout(request, user):
    """Log a LOGOUT action"""
    if not user or not request:
        return None
    
    company = getattr(request, 'current_company', None)
    
    audit_log = AuditLog.objects.create(
        user=user,
        username=user.username,
        object_repr=f"User: {user.username}",
        action='LOGOUT',
        description=f"User {user.username} logged out",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        request_path=request.path,
        request_method=request.method,
        company=company
    )
    
    return audit_log


def log_custom(request, action, description, model_name=None, instance=None, metadata=None):
    """
    Log a custom action.
    
    Args:
        request: Django request object
        action: Action type (CREATE, UPDATE, DELETE, or custom)
        description: Human-readable description
        model_name: Name of the model (optional)
        instance: Model instance (optional)
        metadata: Additional metadata
    """
    user = request.user if request.user.is_authenticated else None
    username = user.username if user else 'Anonymous'
    company = getattr(request, 'current_company', None)
    
    content_type = None
    object_id = None
    object_repr = model_name or 'System'
    
    if instance:
        content_type = ContentType.objects.get_for_model(instance)
        object_id = str(instance.pk)
        object_repr = str(instance)
    
    audit_log = AuditLog.objects.create(
        user=user,
        username=username,
        content_type=content_type,
        object_id=object_id,
        object_repr=object_repr,
        action=action,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        request_path=request.path,
        request_method=request.method,
        company=company,
        metadata=metadata
    )
    
    return audit_log
