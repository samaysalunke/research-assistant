#!/usr/bin/env python3
"""
Simple startup test script to debug Railway deployment issues
"""

import os
import sys
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
    except Exception as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn imported successfully")
    except Exception as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False
    
    try:
        from backend.main import app
        print("✓ Backend main app imported successfully")
    except Exception as e:
        print(f"✗ Backend main app import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_environment():
    """Test environment variables"""
    print("\nTesting environment variables...")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'SUPABASE_SERVICE_ROLE_KEY',
        'ANTHROPIC_API_KEY',
        'OPENAI_API_KEY',
        'DATABASE_URL'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var} is set")
        else:
            print(f"✗ {var} is not set")
    
    port = os.getenv('PORT', '8000')
    print(f"✓ PORT is set to: {port}")

def test_app_startup():
    """Test if the app can be created"""
    print("\nTesting app startup...")
    
    try:
        from backend.main import app
        print("✓ App created successfully")
        print(f"✓ App title: {app.title}")
        print(f"✓ App version: {app.version}")
        return True
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Railway Startup Test ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    
    success = True
    
    if not test_imports():
        success = False
    
    test_environment()
    
    if not test_app_startup():
        success = False
    
    if success:
        print("\n=== All tests passed! ===")
        sys.exit(0)
    else:
        print("\n=== Some tests failed! ===")
        sys.exit(1)
