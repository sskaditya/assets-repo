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
