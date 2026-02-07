"""
Tests for users app (Department, Location, UserProfile)
"""
from django.test import TestCase
from django.contrib.auth.models import User

from .models import Department, Location, UserProfile
from core.models import Company


class DepartmentModelTest(TestCase):
    """Test Department model"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name="Test Company",
            code="TEST-001",
            email="test@example.com"
        )
        
        self.user = User.objects.create_user(
            username='head',
            password='head123'
        )
    
    def test_department_creation(self):
        """Test creating a department"""
        department = Department.objects.create(
            company=self.company,
            name="IT Department",
            code="IT-001",
            head=self.user
        )
        
        self.assertEqual(department.name, "IT Department")
        self.assertEqual(department.head, self.user)
        self.assertTrue(department.is_active)
    
    def test_parent_department(self):
        """Test parent-child department relationship"""
        parent = Department.objects.create(
            company=self.company,
            name="Engineering",
            code="ENG-001"
        )
        
        child = Department.objects.create(
            company=self.company,
            name="Software Engineering",
            code="SOFT-001",
            parent_department=parent
        )
        
        self.assertEqual(child.parent_department, parent)
    
    def test_department_str_representation(self):
        """Test string representation"""
        department = Department.objects.create(
            company=self.company,
            name="IT Department",
            code="IT-001"
        )
        
        expected = f"{self.company.code} - IT-001 - IT Department"
        self.assertEqual(str(department), expected)


class LocationModelTest(TestCase):
    """Test Location model"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name="Test Company",
            code="TEST-001",
            email="test@example.com"
        )
    
    def test_location_creation(self):
        """Test creating a location"""
        location = Location.objects.create(
            company=self.company,
            name="Main Office",
            code="MAIN-001",
            location_type="OFFICE",
            city="New York",
            state="NY",
            country="USA"
        )
        
        self.assertEqual(location.name, "Main Office")
        self.assertEqual(location.location_type, "OFFICE")
        self.assertEqual(location.city, "New York")
        self.assertTrue(location.is_active)
    
    def test_location_str_representation(self):
        """Test string representation"""
        location = Location.objects.create(
            company=self.company,
            name="Main Office",
            code="MAIN-001",
            location_type="OFFICE"
        )
        
        expected = f"{self.company.code} - MAIN-001 - Main Office"
        self.assertEqual(str(location), expected)


class UserProfileModelTest(TestCase):
    """Test UserProfile model"""
    
    def setUp(self):
        """Set up test data"""
        self.company = Company.objects.create(
            name="Test Company",
            code="TEST-001",
            email="test@example.com"
        )
        
        self.department = Department.objects.create(
            company=self.company,
            name="IT Department",
            code="IT-001"
        )
        
        self.location = Location.objects.create(
            company=self.company,
            name="Main Office",
            code="MAIN-001",
            location_type="OFFICE"
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            email='test@example.com'
        )
    
    def test_user_profile_creation(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            company=self.company,
            employee_id='EMP-001',
            department=self.department,
            location=self.location,
            designation='Software Engineer',
            is_asset_custodian=True
        )
        
        self.assertEqual(profile.employee_id, 'EMP-001')
        self.assertEqual(profile.company, self.company)
        self.assertTrue(profile.is_asset_custodian)
    
    def test_user_profile_str_representation(self):
        """Test string representation"""
        profile = UserProfile.objects.create(
            user=self.user,
            company=self.company,
            employee_id='EMP-001'
        )
        
        expected = f"{self.company.code} - {self.user.get_full_name()} (EMP-001)"
        self.assertEqual(str(profile), expected)
    
    def test_reporting_manager_relationship(self):
        """Test reporting manager relationship"""
        manager = User.objects.create_user(
            username='manager',
            password='manager123'
        )
        
        manager_profile = UserProfile.objects.create(
            user=manager,
            company=self.company,
            employee_id='MGR-001'
        )
        
        employee_profile = UserProfile.objects.create(
            user=self.user,
            company=self.company,
            employee_id='EMP-001',
            reporting_manager=manager  # reporting_manager is a User, not UserProfile
        )
        
        self.assertEqual(employee_profile.reporting_manager, manager)
