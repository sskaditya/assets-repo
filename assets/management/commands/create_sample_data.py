from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import Department, Location, UserProfile
from assets.models import AssetCategory, AssetType, Vendor, Asset
from maintenance.models import MaintenanceType


class Command(BaseCommand):
    help = 'Create sample data for testing the asset management system'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create Departments
        self.stdout.write('Creating departments...')
        dept_it, _ = Department.objects.get_or_create(
            code='IT',
            defaults={'name': 'Information Technology', 'description': 'IT Department', 'is_active': True}
        )
        dept_hr, _ = Department.objects.get_or_create(
            code='HR',
            defaults={'name': 'Human Resources', 'description': 'HR Department', 'is_active': True}
        )
        dept_fin, _ = Department.objects.get_or_create(
            code='FIN',
            defaults={'name': 'Finance', 'description': 'Finance Department', 'is_active': True}
        )

        # Create Locations
        self.stdout.write('Creating locations...')
        loc_hq, _ = Location.objects.get_or_create(
            code='HQ',
            defaults={
                'name': 'Head Office',
                'address_line1': '123 Main Street',
                'city': 'Colombo',
                'state': 'Western Province',
                'country': 'Sri Lanka',
                'postal_code': '00100',
                'location_type': 'OFFICE',
                'is_active': True
            }
        )
        loc_wh, _ = Location.objects.get_or_create(
            code='WH1',
            defaults={
                'name': 'Warehouse 1',
                'address_line1': '456 Industrial Road',
                'city': 'Colombo',
                'state': 'Western Province',
                'country': 'Sri Lanka',
                'postal_code': '00200',
                'location_type': 'WAREHOUSE',
                'is_active': True
            }
        )

        # Create Vendors
        self.stdout.write('Creating vendors...')
        vendor_dell, _ = Vendor.objects.get_or_create(
            code='DELL',
            defaults={
                'name': 'Dell Technologies',
                'contact_person': 'John Smith',
                'email': 'sales@dell.com',
                'phone': '+94112345678',
                'city': 'Colombo',
                'state': 'Western Province',
                'country': 'Sri Lanka',
                'vendor_type': 'MANUFACTURER',
                'is_active': True
            }
        )
        vendor_hp, _ = Vendor.objects.get_or_create(
            code='HP',
            defaults={
                'name': 'HP Inc.',
                'contact_person': 'Jane Doe',
                'email': 'sales@hp.com',
                'phone': '+94112345679',
                'city': 'Colombo',
                'state': 'Western Province',
                'country': 'Sri Lanka',
                'vendor_type': 'MANUFACTURER',
                'is_active': True
            }
        )

        # Create Asset Categories
        self.stdout.write('Creating asset categories...')
        cat_electronics, _ = AssetCategory.objects.get_or_create(
            code='ELEC',
            defaults={'name': 'Electronic Assets', 'description': 'Electronic devices and equipment', 'is_active': True}
        )
        cat_it, _ = AssetCategory.objects.get_or_create(
            code='IT',
            defaults={'name': 'IT & Technology', 'description': 'IT infrastructure and technology assets', 'is_active': True}
        )
        cat_furniture, _ = AssetCategory.objects.get_or_create(
            code='FURN',
            defaults={'name': 'Furniture & Office', 'description': 'Office furniture and fixtures', 'is_active': True}
        )

        # Create Asset Types
        self.stdout.write('Creating asset types...')
        type_laptop, _ = AssetType.objects.get_or_create(
            code='LAPTOP',
            defaults={
                'category': cat_electronics,
                'name': 'Laptop',
                'category_type': 'ELECTRONIC',
                'description': 'Portable computers',
                'is_active': True
            }
        )
        type_desktop, _ = AssetType.objects.get_or_create(
            code='DESKTOP',
            defaults={
                'category': cat_electronics,
                'name': 'Desktop Computer',
                'category_type': 'ELECTRONIC',
                'description': 'Desktop computers',
                'is_active': True
            }
        )
        type_printer, _ = AssetType.objects.get_or_create(
            code='PRINTER',
            defaults={
                'category': cat_electronics,
                'name': 'Printer',
                'category_type': 'ELECTRONIC',
                'description': 'Printers and multifunction devices',
                'is_active': True
            }
        )

        # Create Maintenance Types
        self.stdout.write('Creating maintenance types...')
        MaintenanceType.objects.get_or_create(
            code='PM',
            defaults={'name': 'Preventive Maintenance', 'description': 'Regular preventive maintenance', 'is_active': True}
        )
        MaintenanceType.objects.get_or_create(
            code='BM',
            defaults={'name': 'Breakdown Maintenance', 'description': 'Breakdown and repair maintenance', 'is_active': True}
        )
        MaintenanceType.objects.get_or_create(
            code='CAL',
            defaults={'name': 'Calibration', 'description': 'Equipment calibration', 'is_active': True}
        )

        # Create Sample Assets
        self.stdout.write('Creating sample assets...')
        from datetime import date, timedelta
        
        Asset.objects.get_or_create(
            asset_tag='LAP-001',
            defaults={
                'name': 'Dell Latitude 5420',
                'category': cat_electronics,
                'asset_type': type_laptop,
                'description': 'Dell Latitude laptop for office use',
                'make': 'Dell',
                'model': 'Latitude 5420',
                'serial_number': 'DL123456789',
                'status': 'IN_USE',
                'condition': 'GOOD',
                'location': loc_hq,
                'department': dept_it,
                'vendor': vendor_dell,
                'purchase_date': date.today() - timedelta(days=180),
                'purchase_price': 85000.00,
                'warranty_start_date': date.today() - timedelta(days=180),
                'warranty_end_date': date.today() + timedelta(days=185),
                'is_critical': False,
            }
        )

        Asset.objects.get_or_create(
            asset_tag='LAP-002',
            defaults={
                'name': 'HP EliteBook 840',
                'category': cat_electronics,
                'asset_type': type_laptop,
                'description': 'HP EliteBook for management',
                'make': 'HP',
                'model': 'EliteBook 840 G8',
                'serial_number': 'HP987654321',
                'status': 'IN_USE',
                'condition': 'EXCELLENT',
                'location': loc_hq,
                'department': dept_hr,
                'vendor': vendor_hp,
                'purchase_date': date.today() - timedelta(days=90),
                'purchase_price': 95000.00,
                'warranty_start_date': date.today() - timedelta(days=90),
                'warranty_end_date': date.today() + timedelta(days=275),
                'is_critical': False,
            }
        )

        Asset.objects.get_or_create(
            asset_tag='DESK-001',
            defaults={
                'name': 'Dell OptiPlex 7090',
                'category': cat_electronics,
                'asset_type': type_desktop,
                'description': 'Desktop computer for office workstation',
                'make': 'Dell',
                'model': 'OptiPlex 7090',
                'serial_number': 'DL777888999',
                'status': 'IN_USE',
                'condition': 'GOOD',
                'location': loc_hq,
                'department': dept_fin,
                'vendor': vendor_dell,
                'purchase_date': date.today() - timedelta(days=120),
                'purchase_price': 65000.00,
                'warranty_start_date': date.today() - timedelta(days=120),
                'warranty_end_date': date.today() + timedelta(days=245),
                'is_critical': False,
            }
        )

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('You can now login and view the assets in the system.'))
