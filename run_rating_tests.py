#!/usr/bin/env python3
"""
Test runner for FastTTS star rating system
Runs comprehensive tests to ensure the rating system works correctly
"""

import sys
import os
from pathlib import Path
import subprocess
import tempfile
import sqlite3

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['pytest', 'fasthtml']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def test_database_setup():
    """Test database setup and basic operations"""
    print("🔍 Testing database setup...")
    
    try:
        from utils.rating_helpers import initialize_ratings_system, update_word_rating, get_word_rating
        
        # Initialize the rating system
        result = initialize_ratings_system()
        if not result:
            print("❌ Failed to initialize rating system")
            return False
        
        # Test basic operations
        test_word = "测试"
        test_rating = 4.5
        
        # Test rating update
        update_result = update_word_rating(test_word, test_rating)
        if not update_result:
            print("❌ Failed to update word rating")
            return False
        
        # Test rating retrieval
        retrieved_rating = get_word_rating(test_word)
        if retrieved_rating != test_rating:
            print(f"❌ Rating mismatch: expected {test_rating}, got {retrieved_rating}")
            return False
        
        print("✅ Database setup test passed")
        return True
        
    except Exception as e:
        print(f"❌ Database setup test failed: {e}")
        return False

def test_component_rendering():
    """Test UI component rendering"""
    print("🎨 Testing component rendering...")
    
    try:
        from components.star_rating import render_star_rating, render_compact_star_rating
        
        # Test basic star rating component
        component = render_star_rating("测试词", 3.5)
        component_html = str(component)
        
        # Check for required elements
        required_elements = [
            'star-rating',
            'data-chinese-word="测试词"',
            'value="3.5"',
            'min="0.5"',
            'max="5"',
            'step="0.5"'
        ]
        
        for element in required_elements:
            if element not in component_html:
                print(f"❌ Missing required element: {element}")
                return False
        
        # Test compact component
        compact_component = render_compact_star_rating("紧凑测试", 2.0)
        compact_html = str(compact_component)
        
        if 'star-rating-compact' not in compact_html:
            print("❌ Compact component missing compact class")
            return False
        
        print("✅ Component rendering test passed")
        return True
        
    except Exception as e:
        print(f"❌ Component rendering test failed: {e}")
        return False

def test_rating_validation():
    """Test rating value validation"""
    print("✅ Testing rating validation...")
    
    try:
        from utils.rating_helpers import update_word_rating
        
        # Test invalid ratings
        invalid_tests = [
            (5.5, "Rating too high"),
            (0.0, "Rating too low"),
            (2.3, "Rating not in 0.5 increments")
        ]
        
        for invalid_rating, description in invalid_tests:
            result = update_word_rating("测试", invalid_rating)
            if result:
                print(f"❌ {description}: {invalid_rating} should be invalid")
                return False
        
        # Test valid ratings
        valid_ratings = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        for rating in valid_ratings:
            result = update_word_rating("验证测试", rating)
            if not result:
                print(f"❌ Valid rating {rating} was rejected")
                return False
        
        print("✅ Rating validation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Rating validation test failed: {e}")
        return False

def test_import_structure():
    """Test that all modules can be imported correctly"""
    print("📦 Testing import structure...")
    
    try:
        # Test rating helpers
        from utils.rating_helpers import (
            get_word_rating, update_word_rating, get_all_word_ratings,
            get_rating_statistics, initialize_ratings_system
        )
        
        # Test star rating components
        from components.star_rating import (
            render_star_rating, render_compact_star_rating, 
            render_readonly_star_rating, render_rating_summary
        )
        
        # Test that routes can be imported
        from routes.ratings import register_rating_routes
        
        print("✅ Import structure test passed")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Import structure test failed: {e}")
        return False

def run_pytest_tests():
    """Run the comprehensive pytest test suite"""
    print("🧪 Running comprehensive test suite...")
    
    try:
        # Check if pytest is available
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_ratings.py", "-v"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Pytest test suite passed")
            return True
        else:
            print("❌ Pytest test suite failed")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test suite timed out")
        return False
    except Exception as e:
        print(f"❌ Failed to run pytest: {e}")
        print("Note: This is expected if pytest is not installed")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("📁 Testing file structure...")
    
    required_files = [
        "utils/rating_helpers.py",
        "components/star_rating.py", 
        "routes/ratings.py",
        "static/js/rating-manager.js",
        "tests/test_ratings.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ File structure test passed")
    return True

def main():
    """Run all rating system tests"""
    print("🌟 FastTTS Star Rating System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependencies", check_dependencies),
        ("File Structure", test_file_structure),
        ("Import Structure", test_import_structure),
        ("Database Setup", test_database_setup),
        ("Component Rendering", test_component_rendering),
        ("Rating Validation", test_rating_validation),
        ("Comprehensive Tests", run_pytest_tests),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔄 Running {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Star rating system is ready to use.")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)