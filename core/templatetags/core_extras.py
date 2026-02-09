from django import template
from core.models import Company
import json
import pprint as pp

register = template.Library()


@register.filter
def get_all_companies(request):
    """Get all active companies for super admin company selector"""
    return Company.objects.filter(is_deleted=False, is_active=True).order_by('name')


@register.filter
def pprint(value):
    """Pretty print JSON or dict values"""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except:
            return value
    
    if isinstance(value, (dict, list)):
        return pp.pformat(value, indent=2, width=80)


@register.filter
def get_attribute(obj, attr_name):
    """
    Get an attribute from an object dynamically.
    Usage: {{ object|get_attribute:"field_name" }}
    
    Supports:
    - Direct attributes: obj.field_name
    - Dict keys: obj['key']
    - Method calls: obj.method_name()
    - Nested attributes: obj.relation.field
    """
    if obj is None:
        return None
    
    try:
        # Handle nested attributes (e.g., "user.email")
        if '.' in attr_name:
            parts = attr_name.split('.')
            value = obj
            for part in parts:
                value = get_attribute(value, part)
                if value is None:
                    return None
            return value
        
        # Try dictionary access first
        if isinstance(obj, dict):
            return obj.get(attr_name)
        
        # Try getattr for object attributes
        value = getattr(obj, attr_name, None)
        
        # If it's a callable (method), call it
        if callable(value):
            return value()
        
        return value
    except (AttributeError, KeyError, TypeError):
        return None
