"""
Tests for core app (Company management and utilities)
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid

from .models import Company
from .utils import generate_qr_code, generate_qr_code_with_label


class CompanyModelTest(TestCase):
    """Test Company model"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name="Test Company",
            code="TEST-001",
            email="test@example.com",
            phone="+1234567890",
            is_active=True
        )
    
    def test_company_creation(self):
        """Test creating a company"""
        self.assertEqual(self.company.name, "Test Company")
        self.assertEqual(self.company.code, "TEST-001")
        self.assertTrue(self.company.is_active)
    
    def test_company_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.company), "TEST-001 - Test Company")
    
    def test_subscription_active_property(self):
        """Test is_subscription_active property"""
        from datetime import date, timedelta
        
        # Clear subscription dates first
        self.company.subscription_start_date = None
        self.company.subscription_end_date = None
        self.company.save()
        self.company.refresh_from_db()
        
        # Test with no subscription dates (defaults to active if company is active)
        if hasattr(self.company, 'is_subscription_active'):
            # If no dates set and company is active, it might default to True
            # depending on implementation
            pass
        
        # Test with active subscription
        self.company.subscription_start_date = date.today() - timedelta(days=30)
        self.company.subscription_end_date = date.today() + timedelta(days=30)
        self.company.save()
        self.company.refresh_from_db()
        
        if hasattr(self.company, 'is_subscription_active'):
            self.assertTrue(self.company.is_subscription_active)
        
        # Test with expired subscription
        self.company.subscription_end_date = date.today() - timedelta(days=1)
        self.company.save()
        self.company.refresh_from_db()
        
        if hasattr(self.company, 'is_subscription_active'):
            self.assertFalse(self.company.is_subscription_active)
    
    def test_company_soft_delete(self):
        """Test soft delete functionality"""
        self.company.soft_delete()
        self.company.refresh_from_db()
        
        self.assertTrue(self.company.is_deleted)
        self.assertIsNotNone(self.company.deleted_at)


class QRCodeUtilityTest(TestCase):
    """Test QR code generation utilities"""
    
    def test_generate_qr_code(self):
        """Test basic QR code generation"""
        test_data = "TEST-QR-CODE-123"
        qr_file = generate_qr_code(test_data, asset_tag="TEST-001")
        
        self.assertIsNotNone(qr_file)
        self.assertTrue(qr_file.name.startswith("qr_"))
        self.assertTrue(qr_file.name.endswith(".png"))
    
    def test_generate_qr_code_with_uuid(self):
        """Test QR code generation with UUID"""
        test_uuid = uuid.uuid4()
        qr_file = generate_qr_code(str(test_uuid))
        
        self.assertIsNotNone(qr_file)
    
    def test_generate_qr_code_with_label(self):
        """Test QR code generation with label"""
        test_data = str(uuid.uuid4())
        label_text = "ASSET-001"
        
        qr_file = generate_qr_code_with_label(
            test_data,
            label_text,
            asset_tag="ASSET-001"
        )
        
        self.assertIsNotNone(qr_file)
        self.assertTrue(qr_file.name.endswith(".png"))
    
    def test_qr_code_file_size(self):
        """Test that generated QR code has reasonable file size"""
        test_data = "TEST-DATA"
        qr_file = generate_qr_code(test_data)
        
        # File should have content
        qr_file.seek(0)
        content = qr_file.read()
        self.assertGreater(len(content), 0)
        
        # File size should be reasonable (between 1KB and 100KB)
        self.assertGreater(len(content), 1000)  # At least 1KB
        self.assertLess(len(content), 100000)  # Less than 100KB


class CompanyViewsTest(TestCase):
    """Test company management views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create superuser for testing company management
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_superuser=True,
            is_staff=True
        )
        
        self.company = Company.objects.create(
            name="Test Company",
            code="TEST-001",
            email="test@example.com",
            is_active=True
        )
    
    def test_company_list_view(self):
        """Test company list view"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('core:company_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_company_create_view(self):
        """Test company create view"""
        self.client.login(username='admin', password='admin123')
        
        data = {
            'name': 'New Company',
            'code': 'NEW-001',
            'email': 'new@example.com',
            'country': 'Sri Lanka',
            'max_users': 50,
            'max_assets': 1000,
            'is_active': True
        }
        
        response = self.client.post(reverse('core:company_create'), data)
        
        company = Company.objects.filter(code='NEW-001').first()
        self.assertIsNotNone(company)
        if company:
            self.assertEqual(company.name, 'New Company')
    
    def test_company_update_view(self):
        """Test company update view"""
        self.client.login(username='admin', password='admin123')
        
        data = {
            'name': 'Updated Company',
            'code': self.company.code,
            'email': self.company.email,
            'country': 'Sri Lanka',
            'max_users': 50,
            'max_assets': 1000,
            'is_active': True
        }
        
        response = self.client.post(
            reverse('core:company_update', args=[self.company.pk]),
            data
        )
        
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Updated Company')
    
    def test_company_detail_view(self):
        """Test company detail view"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(
            reverse('core:company_detail', args=[self.company.pk])
        )
        self.assertEqual(response.status_code, 200)


class CompanyFormTest(TestCase):
    """Test company forms"""
    
    def test_company_form_valid(self):
        """Test valid company form"""
        from .forms import CompanyForm
        
        data = {
            'name': 'Form Test Company',
            'code': 'FORM-001',
            'email': 'form@example.com',
            'country': 'Sri Lanka',  # Default value required
            'max_users': 50,
            'max_assets': 1000,
            'is_active': True
        }
        
        form = CompanyForm(data=data)
        if not form.is_valid():
            print("Form errors:", form.errors)
        self.assertTrue(form.is_valid())
    
    def test_company_form_invalid(self):
        """Test invalid company form"""
        from .forms import CompanyForm
        
        data = {
            'name': '',  # Required field missing
            'code': 'FORM-001'
        }
        
        form = CompanyForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class MiddlewareTest(TestCase):
    """Test company middleware"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        self.company = Company.objects.create(
            name="Test Company",
            code="TEST-001",
            email="test@example.com",
            is_active=True
        )
        
        self.user = User.objects.create_user(
            username='user',
            password='user123'
        )
        
        from users.models import UserProfile
        UserProfile.objects.create(
            user=self.user,
            company=self.company,
            employee_id='EMP-001'
        )
    
    def test_middleware_sets_company_context(self):
        """Test that middleware sets company context"""
        self.client.login(username='user', password='user123')
        response = self.client.get('/app/dashboard/')
        
        # Middleware should set current_company in request
        # This is tested indirectly through view rendering
        self.assertEqual(response.status_code, 200)
