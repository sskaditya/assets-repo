"""
Utility functions for asset management
"""
from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


def calculate_straight_line_depreciation(purchase_price, salvage_value, useful_life_years):
    """
    Calculate depreciation using Straight Line Method
    Annual Depreciation = (Purchase Price - Salvage Value) / Useful Life
    """
    if not all([purchase_price, useful_life_years]):
        return None
    
    salvage = salvage_value or Decimal('0.00')
    annual_depreciation = (purchase_price - salvage) / useful_life_years
    return annual_depreciation


def calculate_reducing_balance_depreciation(purchase_price, depreciation_rate, years_elapsed):
    """
    Calculate depreciation using Reducing Balance Method
    Annual Depreciation = Book Value × Depreciation Rate
    """
    if not all([purchase_price, depreciation_rate]):
        return None
    
    book_value = purchase_price
    for _ in range(years_elapsed):
        depreciation = book_value * (depreciation_rate / 100)
        book_value -= depreciation
    
    return purchase_price - book_value


def calculate_current_book_value(asset):
    """
    Calculate current book value of an asset
    """
    if not asset.purchase_price or not asset.purchase_date:
        return asset.purchase_price
    
    years_elapsed = (date.today() - asset.purchase_date).days / 365.25
    
    if asset.depreciation_rate:
        # Use reducing balance method if rate is specified
        total_depreciation = calculate_reducing_balance_depreciation(
            asset.purchase_price,
            asset.depreciation_rate,
            int(years_elapsed)
        )
    elif asset.useful_life_years:
        # Use straight line method
        annual_depreciation = calculate_straight_line_depreciation(
            asset.purchase_price,
            asset.salvage_value or Decimal('0.00'),
            asset.useful_life_years
        )
        total_depreciation = annual_depreciation * Decimal(str(years_elapsed))
    else:
        return asset.purchase_price
    
    salvage = asset.salvage_value or Decimal('0.00')
    book_value = asset.purchase_price - (total_depreciation or Decimal('0.00'))
    
    # Book value should not go below salvage value
    return max(book_value, salvage)


def calculate_depreciation_schedule(asset):
    """
    Generate depreciation schedule for an asset
    Returns list of yearly depreciation values
    """
    if not all([asset.purchase_price, asset.purchase_date, asset.useful_life_years]):
        return []
    
    schedule = []
    salvage = asset.salvage_value or Decimal('0.00')
    
    if asset.depreciation_rate:
        # Reducing balance method
        book_value = asset.purchase_price
        for year in range(asset.useful_life_years):
            depreciation = book_value * (asset.depreciation_rate / 100)
            book_value -= depreciation
            if book_value < salvage:
                depreciation = book_value + depreciation - salvage
                book_value = salvage
            
            schedule.append({
                'year': year + 1,
                'depreciation': depreciation,
                'book_value': book_value
            })
            
            if book_value <= salvage:
                break
    else:
        # Straight line method
        annual_depreciation = calculate_straight_line_depreciation(
            asset.purchase_price,
            salvage,
            asset.useful_life_years
        )
        book_value = asset.purchase_price
        
        for year in range(asset.useful_life_years):
            book_value -= annual_depreciation
            schedule.append({
                'year': year + 1,
                'depreciation': annual_depreciation,
                'book_value': max(book_value, salvage)
            })
    
    return schedule


def get_assets_due_for_maintenance(company, days_ahead=30):
    """
    Get assets that are due for maintenance in the next X days
    """
    from maintenance.models import MaintenanceSchedule
    from django.utils import timezone
    
    today = timezone.now().date()
    future_date = today + timedelta(days=days_ahead)
    
    schedules = MaintenanceSchedule.objects.filter(
        asset__company=company,
        asset__is_deleted=False,
        is_active=True,
        next_due_date__gte=today,
        next_due_date__lte=future_date
    ).select_related('asset', 'maintenance_type').order_by('next_due_date')
    
    return schedules


def get_assets_warranty_expiring(company, days_ahead=30):
    """
    Get assets whose warranty is expiring in the next X days
    """
    from assets.models import Asset
    from django.utils import timezone
    
    today = timezone.now().date()
    future_date = today + timedelta(days=days_ahead)
    
    assets = Asset.objects.filter(
        company=company,
        is_deleted=False,
        warranty_end_date__gte=today,
        warranty_end_date__lte=future_date
    ).order_by('warranty_end_date')
    
    return assets


def get_assets_amc_expiring(company, days_ahead=30):
    """
    Get assets whose AMC is expiring in the next X days
    """
    from assets.models import Asset
    from django.utils import timezone
    
    today = timezone.now().date()
    future_date = today + timedelta(days=days_ahead)
    
    assets = Asset.objects.filter(
        company=company,
        is_deleted=False,
        amc_end_date__gte=today,
        amc_end_date__lte=future_date
    ).order_by('amc_end_date')
    
    return assets


def calculate_asset_age(purchase_date):
    """
    Calculate asset age in years and months
    """
    if not purchase_date:
        return None
    
    today = date.today()
    delta = relativedelta(today, purchase_date)
    
    return {
        'years': delta.years,
        'months': delta.months,
        'total_days': (today - purchase_date).days
    }


def get_asset_utilization_rate(asset):
    """
    Calculate asset utilization rate based on usage
    This can be enhanced based on your specific metrics
    """
    if asset.status == 'IN_USE':
        return 100
    elif asset.status in ['PLANNING', 'ORDERED', 'IN_STOCK']:
        return 0
    elif asset.status == 'UNDER_MAINTENANCE':
        return 0
    elif asset.status in ['RETIRED', 'DISPOSED']:
        return 0
    else:
        return 50  # Partial utilization


def generate_asset_report_data(company):
    """
    Generate comprehensive asset report data
    """
    from assets.models import Asset
    from django.db.models import Count, Sum, Avg, Q
    
    assets = Asset.objects.filter(company=company, is_deleted=False)
    
    report = {
        'total_assets': assets.count(),
        'total_value': assets.aggregate(Sum('purchase_price'))['purchase_price__sum'] or 0,
        'by_status': assets.values('status').annotate(count=Count('id')),
        'by_category': assets.values('category__name').annotate(count=Count('id')),
        'by_location': assets.values('location__name').annotate(count=Count('id')),
        'by_condition': assets.values('condition').annotate(count=Count('id')),
        'critical_assets': assets.filter(is_critical=True).count(),
        'under_warranty': assets.filter(
            warranty_end_date__gte=date.today()
        ).count(),
        'under_amc': assets.filter(
            amc_end_date__gte=date.today()
        ).count(),
    }
    
    return report
