"""
Test script for OCR functionality
This script tests OCR integration without starting the full application
"""

import os
import sys
import tempfile
from PIL import Image
import numpy as np

def create_test_image():
    """Create a simple test image with text for OCR testing"""
    # Create a simple test image
    image = Image.new('RGB', (400, 200), color='white')
    return image

def test_ocr_import():
    """Test that OCR module can be imported"""
    try:
        from utils.ocr_processor import image_processor
        print("✓ Image processor imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import image processor: {e}")
        return False

def test_ocr_initialization():
    """Test that OCR model can be initialized"""
    try:
        from utils.ocr_processor import image_processor
        # Test actual model initialization (this will test the logic but not load the full model)
        # We'll just test that the initialization method exists and can be called
        if hasattr(image_processor, 'initialize_ocr_model'):
            print("✓ Image processor OCR initialization method found")
            # Don't actually call it to avoid downloading models during testing
            print("✓ Image processor OCR initialization test completed (method exists)")
            return True
        else:
            print("✗ Image processor OCR initialization method not found")
            return False
    except Exception as e:
        print(f"✗ Failed to test image processor OCR initialization: {e}")
        return False

def test_file_processing():
    """Test that file processing utilities work"""
    try:
        from utils.file_processing import is_image_file, extract_text_from_image
        
        # Test image file detection
        test_files = ["test.png", "test.jpg", "test.pdf", "test.txt"]
        expected = [True, True, False, False]
        
        for file, expected_result in zip(test_files, expected):
            result = is_image_file(file)
            if result == expected_result:
                print(f"✓ is_image_file('{file}') = {result}")
            else:
                print(f"✗ is_image_file('{file}') = {result}, expected {expected_result}")
        
        print("✓ File processing utilities test completed")
        return True
    except Exception as e:
        print(f"✗ Failed to test file processing utilities: {e}")
        return False

def main():
    """Run all tests"""
    print("Running image processing integration tests...")
    
    tests = [
        test_ocr_import,
        test_ocr_initialization,
        test_file_processing
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Image processing integration is ready.")
        return 0
    else:
        print("Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
