#!/usr/bin/env python
"""
Test runner script for the asset management system
Runs all tests and generates a coverage report
"""
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Setup Django settings for tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assetz.test_settings')
django.setup()

from django.test.runner import DiscoverRunner
from django.conf import settings


def run_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("RUNNING ASSET MANAGEMENT SYSTEM TESTS")
    print("="*70 + "\n")
    
    # Configure test runner
    test_runner = DiscoverRunner(
        verbosity=2,
        interactive=False,
        keepdb=False,
        failfast=False
    )
    
    # Run tests
    failures = test_runner.run_tests([
        'assets.tests',
        'core.tests',
        'users.tests'
    ])
    
    print("\n" + "="*70)
    if failures:
        print(f"TESTS FAILED: {failures} test(s) failed")
    else:
        print("ALL TESTS PASSED ✓")
    print("="*70 + "\n")
    
    return failures


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(bool(exit_code))
