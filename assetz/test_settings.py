"""
Test settings for the asset management system
Overrides settings for test environment
"""
from .settings import *

# Override database settings for tests
# Remove schema option which causes issues with test database creation
DATABASES['default']['OPTIONS'] = {}
DATABASES['default']['TEST'] = {
    'NAME': 'test_assetz',
}

# Use simpler password hashers for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations for faster tests (optional)
# Uncomment if tests are slow
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     
#     def __getitem__(self, item):
#         return None
# 
# MIGRATION_MODULES = DisableMigrations()

# Email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Media files for tests (use temporary directory)
import tempfile
MEDIA_ROOT = tempfile.mkdtemp()

# Disable debug toolbar in tests
DEBUG = False

# Simplify logging for tests
LOGGING_CONFIG = None
