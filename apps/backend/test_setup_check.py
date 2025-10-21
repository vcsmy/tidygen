#!/usr/bin/env python
"""
Quick setup check for the testing environment.
This script verifies that all testing dependencies are properly installed and configured.
"""

import sys
import os

def check_imports():
    """Check if all required testing packages can be imported."""
    try:
        import pytest
        print("✅ pytest available")
    except ImportError:
        print("❌ pytest not available")
        return False
    
    try:
        import django
        print("✅ django available")
    except ImportError:
        print("❌ django not available")
        return False
    
    try:
        import playwright
        print("✅ playwright available")
    except ImportError:
        print("❌ playwright not available")
        return False
    
    try:
        import flake8
        print("✅ flake8 available")
    except ImportError:
        print("❌ flake8 not available")
        return False
    
    try:
        import black
        print("✅ black available")
    except ImportError:
        print("❌ black not available")
        return False
    
    try:
        import mypy
        print("✅ mypy available")
    except ImportError:
        print("❌ mypy not available")
        return False
    
    return True

def check_files():
    """Check if all required configuration files exist."""
    files_to_check = [
        'pytest.ini',
        '.flake8',
        'pyproject.toml',
        'run_tests.py',
        'apps/core/tests/__init__.py',
        'apps/core/tests/test_models.py',
        'apps/core/tests/test_views.py',
        'e2e_tests/test_homepage_flow.py',
        'e2e_tests/conftest.py',
    ]
    
    all_good = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_good = False
    
    return all_good

def main():
    """Main check function."""
    print("🧪 Testing Setup Check")
    print("=" * 40)
    
    print("\n📦 Checking package imports...")
    imports_ok = check_imports()
    
    print("\n📁 Checking configuration files...")
    files_ok = check_files()
    
    print("\n" + "=" * 40)
    if imports_ok and files_ok:
        print("🎉 Testing setup looks good!")
        return 0
    else:
        print("⚠️  Some issues found in testing setup")
        return 1

if __name__ == "__main__":
    sys.exit(main())
