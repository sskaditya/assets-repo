"""
Comprehensive tests for the assets app
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from datetime import date, timedelta
import uuid
import os

from .models import (
    Asset, AssetCategory, AssetType, Vendor, 
    AssetDocument, AssetHistory, AssetTransfer, AssetDisposal
)
from core.models import Company
from users.models import Department, Location, UserProfile


class BaseTestCase(TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        """Set up test data"""
        # Create test company
        self.company = Company.objects.create(
            name="Test Company",
            code="TEST-001",
            email="test@example.com",
            is_active=True
        )
        
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            is_superuser=True,
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            password='user123',
            email='user@test.com'
        )
        
        # Create user profile for regular user
        self.user_profile = UserProfile.objects.create(
            user=self.regular_user,
            company=self.company,
            employee_id='EMP-001'
        )
        
        # Create test department and location
        self.department = Department.objects.create(
            company=self.company,
            name="IT Department",
            code="IT-001"
        )
        
        self.location = Location.objects.create(
            company=self.company,
            name="Main Office",
            code="LOC-001",
            location_type="OFFICE"
        )
        
        # Create test category
        self.category = AssetCategory.objects.create(
            company=self.company,
            name="Electronics",
            code="ELEC-001"
        )
        
        # Create test asset type
        self.asset_type = AssetType.objects.create(
            company=self.company,
            category=self.category,
            name="Laptop",
            code="LAP-001",
        )
        
        # Create test vendor
        self.vendor = Vendor.objects.create(
            company=self.company,
            name="Dell Inc.",
            code="VEND-001",
            vendor_type="SUPPLIER"
        )
        
        self.client = Client()


class AssetModelTest(BaseTestCase):
    """Test Asset model"""
    
    def test_asset_creation(self):
        """Test creating an asset"""
        asset = Asset.objects.create(
            company=self.company,
            asset_tag="ASSET-001",
            name="Dell Laptop",
            asset_type=self.asset_type,
            category=self.category,
            status="IN_STOCK"
        )
        
        self.assertEqual(asset.name, "Dell Laptop")
        self.assertEqual(asset.status, "IN_STOCK")
        self.assertIsNotNone(asset.qr_code)
        self.assertIsInstance(asset.qr_code, uuid.UUID)
    
    def test_asset_qr_code_unique(self):
        """Test that QR codes are unique"""
        asset1 = Asset.objects.create(
            company=self.company,
            asset_tag="ASSET-001",
            name="Asset 1",
            asset_type=self.asset_type,
            category=self.category
        )
        
        asset2 = Asset.objects.create(
            company=self.company,
            asset_tag="ASSET-002",
            name="Asset 2",
            asset_type=self.asset_type,
            category=self.category
        )
        
        self.assertNotEqual(asset1.qr_code, asset2.qr_code)
    
    def test_asset_soft_delete(self):
        """Test soft delete functionality"""
        asset = Asset.objects.create(
            company=self.company,
            asset_tag="ASSET-001",
            name="Test Asset",
            asset_type=self.asset_type,
            category=self.category
        )
        
        asset.soft_delete()
        asset.refresh_from_db()
        
        self.assertTrue(asset.is_deleted)
        self.assertIsNotNone(asset.deleted_at)
    
    def test_asset_str_representation(self):
        """Test string representation"""
        asset = Asset.objects.create(
            company=self.company,
            asset_tag="ASSET-001",
            name="Test Asset",
            asset_type=self.asset_type,
            category=self.category
        )
        
        expected = f"{self.company.code} - ASSET-001 - Test Asset"
        self.assertEqual(str(asset), expected)


class AssetCategoryModelTest(BaseTestCase):
    """Test AssetCategory model"""
    
    def test_category_creation(self):
        """Test creating a category"""
        category = AssetCategory.objects.create(
            company=self.company,
            name="Furniture",
            code="FURN-001"
        )
        
        self.assertEqual(category.name, "Furniture")
        self.assertTrue(category.is_active)
    
    def test_parent_category(self):
        """Test parent-child category relationship"""
        parent = AssetCategory.objects.create(
            company=self.company,
            name="Office Equipment",
            code="OFFICE-001"
        )
        
        child = AssetCategory.objects.create(
            company=self.company,
            name="Computers",
            code="COMP-001",
            parent_category=parent
        )
        
        self.assertEqual(child.parent_category, parent)
        self.assertIn(child, parent.sub_categories.all())


class AssetTypeModelTest(BaseTestCase):
    """Test AssetType model"""
    
    def test_asset_type_creation(self):
        """Test creating an asset type"""
        asset_type = AssetType.objects.create(
            company=self.company,
            category=self.category,
            name="Desktop Computer",
            code="DESK-001",
            requires_calibration=False,
            requires_insurance=True
        )
        
        self.assertEqual(asset_type.name, "Desktop Computer")
        self.assertTrue(asset_type.requires_insurance)
        self.assertFalse(asset_type.requires_calibration)


class VendorModelTest(BaseTestCase):
    """Test Vendor model"""
    
    def test_vendor_creation(self):
        """Test creating a vendor"""
        vendor = Vendor.objects.create(
            company=self.company,
            name="HP Inc.",
            code="HP-001",
            vendor_type="MANUFACTURER",
            email="hp@example.com",
            phone="+1234567890"
        )
        
        self.assertEqual(vendor.name, "HP Inc.")
        self.assertEqual(vendor.vendor_type, "MANUFACTURER")
        self.assertTrue(vendor.is_active)


class QRCodeGenerationTest(BaseTestCase):
    """Test QR code generation"""
    
    def test_qr_code_generated_on_asset_creation(self):
        """Test that QR code is generated when asset is created"""
        asset = Asset.objects.create(
            company=self.company,
            asset_tag="ASSET-QR-001",
            name="Test Asset",
            asset_type=self.asset_type,
            category=self.category
        )
        
        # QR code UUID should be generated
        self.assertIsNotNone(asset.qr_code)
        
        # Check if signal was triggered (qr_code_image might be generated)
        # Note: In test environment, file system operations might be mocked
        self.assertTrue(isinstance(asset.qr_code, uuid.UUID))


class AssetHistoryTest(BaseTestCase):
    """Test AssetHistory model"""
    
    def test_history_created_on_asset_creation(self):
        """Test that history entry is created when asset is created"""
        asset = Asset.objects.create(
            company=self.company,
            asset_tag="ASSET-HIST-001",
            name="Test Asset",
            asset_type=self.asset_type,
            category=self.category
        )
        
        # Check if history entry was created
        history = AssetHistory.objects.filter(asset=asset)
        self.assertTrue(history.exists())
        
        first_entry = history.first()
        self.assertEqual(first_entry.action_type, 'CREATED')


class AssetViewsTest(BaseTestCase):
    """Test asset views"""
    
    def test_dashboard_view_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(reverse('assets:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_view_authenticated(self):
        """Test dashboard view with authenticated user"""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('assets:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_asset_list_view(self):
        """Test asset list view"""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('assets:asset_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assets/asset_list.html')
    
    def test_asset_create_view_get(self):
        """Test asset create view GET request"""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('assets:asset_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assets/asset_form.html')
    
    def test_asset_create_view_post(self):
        """Test asset create view POST request"""
        self.client.login(username='user', password='user123')
        
        data = {
            'asset_tag': 'TEST-CREATE-001',
            'name': 'New Test Asset',
            'asset_type': self.asset_type.id,
            'category': self.category.id,
            'status': 'IN_STOCK',
            'condition': 'GOOD'
        }
        
        response = self.client.post(reverse('assets:asset_create'), data)
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check if asset was created
        asset = Asset.objects.filter(asset_tag='TEST-CREATE-001').first()
        self.assertIsNotNone(asset)
        self.assertEqual(asset.name, 'New Test Asset')
    
    def test_asset_detail_view(self):
        """Test asset detail view"""
        asset = Asset.objects.create(
            company=self.company,
            asset_tag="DETAIL-001",
            name="Detail Test Asset",
            asset_type=self.asset_type,
            category=self.category
        )
        
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('assets:asset_detail', args=[asset.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, asset.name)
    
    def test_asset_update_view(self):
        """Test asset update view"""
        asset = Asset.objects.create(
            company=self.company,
            asset_tag="UPDATE-001",
            name="Original Name",
            asset_type=self.asset_type,
            category=self.category
        )
        
        self.client.login(username='user', password='user123')
        
        data = {
            'asset_tag': asset.asset_tag,
            'name': 'Updated Name',
            'asset_type': self.asset_type.id,
            'category': self.category.id,
            'status': 'IN_USE',
            'condition': 'GOOD'
        }
        
        response = self.client.post(
            reverse('assets:asset_update', args=[asset.pk]), 
            data
        )
        
        asset.refresh_from_db()
        self.assertEqual(asset.name, 'Updated Name')
    
    def test_asset_delete_view(self):
        """Test asset delete view"""
        asset = Asset.objects.create(
            company=self.company,
            asset_tag="DELETE-001",
            name="To Delete",
            asset_type=self.asset_type,
            category=self.category
        )
        
        self.client.login(username='user', password='user123')
        response = self.client.post(
            reverse('assets:asset_delete', args=[asset.pk])
        )
        
        asset.refresh_from_db()
        self.assertTrue(asset.is_deleted)


class CategoryViewsTest(BaseTestCase):
    """Test category views"""
    
    def test_category_list_view(self):
        """Test category list view"""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('assets:category_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_category_create_view(self):
        """Test category create view"""
        self.client.login(username='user', password='user123')
        
        data = {
            'code': 'NEW-CAT-001',
            'name': 'New Category',
            'is_active': True
        }
        
        response = self.client.post(reverse('assets:category_create'), data)
        
        category = AssetCategory.objects.filter(code='NEW-CAT-001').first()
        self.assertIsNotNone(category)
        self.assertEqual(category.name, 'New Category')
    
    def test_category_update_view(self):
        """Test category update view"""
        category = AssetCategory.objects.create(
            company=self.company,
            name="Old Category",
            code="OLD-001"
        )
        
        self.client.login(username='user', password='user123')
        
        data = {
            'code': category.code,
            'name': 'Updated Category',
            'is_active': True
        }
        
        response = self.client.post(
            reverse('assets:category_update', args=[category.pk]),
            data
        )
        
        category.refresh_from_db()
        self.assertEqual(category.name, 'Updated Category')


class TypeViewsTest(BaseTestCase):
    """Test asset type views"""
    
    def test_type_list_view(self):
        """Test type list view"""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('assets:type_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_type_create_view(self):
        """Test type create view"""
        self.client.login(username='user', password='user123')
        
        data = {
            'code': 'NEW-TYPE-001',
            'name': 'New Type',
            'category': self.category.id,
            'requires_calibration': False,
            'requires_insurance': True,
            'is_active': True
        }
        
        response = self.client.post(reverse('assets:type_create'), data)
        
        asset_type = AssetType.objects.filter(code='NEW-TYPE-001').first()
        self.assertIsNotNone(asset_type)
        self.assertEqual(asset_type.name, 'New Type')


class VendorViewsTest(BaseTestCase):
    """Test vendor views"""
    
    def test_vendor_list_view(self):
        """Test vendor list view"""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('assets:vendor_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_vendor_create_view(self):
        """Test vendor create view"""
        self.client.login(username='user', password='user123')
        
        data = {
            'code': 'NEW-VEND-001',
            'name': 'New Vendor',
            'vendor_type': 'SUPPLIER',
            'country': 'India',  # Default value required
            'is_active': True
        }
        
        response = self.client.post(reverse('assets:vendor_create'), data)
        
        vendor = Vendor.objects.filter(code='NEW-VEND-001').first()
        self.assertIsNotNone(vendor)
        self.assertEqual(vendor.name, 'New Vendor')


class AssetFormTest(BaseTestCase):
    """Test asset forms"""
    
    def test_asset_form_valid(self):
        """Test valid asset form"""
        from .forms import AssetForm
        
        data = {
            'asset_tag': 'FORM-TEST-001',
            'name': 'Form Test Asset',
            'asset_type': self.asset_type.id,
            'category': self.category.id,
            'status': 'IN_STOCK',
            'condition': 'GOOD'
        }
        
        form = AssetForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_asset_form_invalid(self):
        """Test invalid asset form"""
        from .forms import AssetForm
        
        data = {
            'asset_tag': '',  # Required field missing
            'name': 'Form Test Asset',
        }
        
        form = AssetForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('asset_tag', form.errors)


class CategoryFormTest(BaseTestCase):
    """Test category forms"""
    
    def test_category_form_valid(self):
        """Test valid category form"""
        from .forms import AssetCategoryForm
        
        data = {
            'code': 'FORM-CAT-001',
            'name': 'Form Test Category',
            'is_active': True
        }
        
        form = AssetCategoryForm(data=data, company=self.company)
        self.assertTrue(form.is_valid())


class TypeFormTest(BaseTestCase):
    """Test asset type forms"""
    
    def test_type_form_valid(self):
        """Test valid type form"""
        from .forms import AssetTypeForm
        
        data = {
            'code': 'FORM-TYPE-001',
            'name': 'Form Test Type',
            'category': self.category.id,
            'is_active': True
        }
        
        form = AssetTypeForm(data=data, company=self.company)
        self.assertTrue(form.is_valid())


class VendorFormTest(BaseTestCase):
    """Test vendor forms"""
    
    def test_vendor_form_valid(self):
        """Test valid vendor form"""
        from .forms import VendorForm
        
        data = {
            'code': 'FORM-VEND-001',
            'name': 'Form Test Vendor',
            'vendor_type': 'SUPPLIER',
            'country': 'India',  # Default value required
            'is_active': True
        }
        
        form = VendorForm(data=data)
        self.assertTrue(form.is_valid())


class QRScannerTest(BaseTestCase):
    """Test QR scanner functionality"""
    
    def test_qr_scanner_view(self):
        """Test QR scanner view"""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('assets:qr_scanner'))
        self.assertEqual(response.status_code, 200)
    
    def test_asset_lookup_api(self):
        """Test asset lookup API"""
        asset = Asset.objects.create(
            company=self.company,
            asset_tag="QR-TEST-001",
            name="QR Test Asset",
            asset_type=self.asset_type,
            category=self.category
        )
        
        self.client.login(username='user', password='user123')
        response = self.client.get(
            reverse('assets:asset_lookup_api'),
            {'code': str(asset.qr_code)}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['asset']['asset_tag'], 'QR-TEST-001')


class AuditTrailTest(BaseTestCase):
    """Test audit trail functionality"""
    
    def test_audit_trail_view(self):
        """Test audit trail view"""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('assets:audit_trail'))
        self.assertEqual(response.status_code, 200)
    
    def test_asset_history_recorded(self):
        """Test that asset history is recorded"""
        asset = Asset.objects.create(
            company=self.company,
            asset_tag="AUDIT-001",
            name="Audit Test",
            asset_type=self.asset_type,
            category=self.category
        )
        
        # Check history was created
        history_count = AssetHistory.objects.filter(asset=asset).count()
        self.assertGreater(history_count, 0)


class IntegrationTest(BaseTestCase):
    """Integration tests for complete workflows"""
    
    def test_complete_asset_workflow(self):
        """Test complete asset creation and management workflow"""
        self.client.login(username='user', password='user123')
        
        # 1. Create asset
        asset_data = {
            'asset_tag': 'WORKFLOW-001',
            'name': 'Workflow Test Asset',
            'asset_type': self.asset_type.id,
            'category': self.category.id,
            'status': 'IN_STOCK',
            'condition': 'GOOD',
            'location': self.location.id,
            'department': self.department.id
        }
        
        response = self.client.post(reverse('assets:asset_create'), asset_data)
        self.assertEqual(response.status_code, 302)
        
        # 2. Verify asset exists
        asset = Asset.objects.get(asset_tag='WORKFLOW-001')
        self.assertIsNotNone(asset)
        self.assertIsNotNone(asset.qr_code)
        
        # 3. View asset detail
        response = self.client.get(reverse('assets:asset_detail', args=[asset.pk]))
        self.assertEqual(response.status_code, 200)
        
        # 4. Update asset
        update_data = asset_data.copy()
        update_data['status'] = 'IN_USE'
        response = self.client.post(
            reverse('assets:asset_update', args=[asset.pk]),
            update_data
        )
        
        asset.refresh_from_db()
        self.assertEqual(asset.status, 'IN_USE')
        
        # 5. Check history
        history = AssetHistory.objects.filter(asset=asset)
        self.assertTrue(history.exists())


class PermissionTest(BaseTestCase):
    """Test permissions and access control"""
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users are redirected"""
        response = self.client.get(reverse('assets:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))
    
    def test_authenticated_access(self):
        """Test authenticated user access"""
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('assets:dashboard'))
        self.assertEqual(response.status_code, 200)
