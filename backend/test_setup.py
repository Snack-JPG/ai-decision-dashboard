#!/usr/bin/env python3
"""
Test script to verify the backend setup is working correctly
"""
import os
from database import init_database, get_db_session
from models import Dataset, DatasetColumn
from datetime import datetime

def test_database_setup():
    """Test database creation and basic operations"""
    print("🔧 Testing database setup...")
    
    # Initialize database
    init_database()
    print("✅ Database tables created successfully")
    
    # Test database connection
    try:
        db = get_db_session()
        
        # Try to query (should be empty initially)
        datasets = db.query(Dataset).all()
        print(f"✅ Database connection successful. Found {len(datasets)} datasets")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "main.py",
        "database.py", 
        "models.py",
        "ingestion.py",
        "requirements.txt",
        "run.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 AI Decision Dashboard Backend Setup Test")
    print("=" * 50)
    
    success = True
    
    # Test file structure
    success &= test_file_structure()
    
    # Test database setup  
    success &= test_database_setup()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Backend is ready.")
        print("\nTo start the server, run:")
        print("  python3 run.py")
        print("\nAPI docs will be at: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    return success

if __name__ == "__main__":
    main()