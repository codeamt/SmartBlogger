"""
Test script for MLX functionality on Apple Silicon
This script tests MLX integration without starting the full application
"""

import sys

def test_mlx_import():
    """Test that MLX can be imported"""
    try:
        import mlx.core as mx
        import mlx.nn as nn
        import mlx.optimizers as optim
        print("✓ MLX imported successfully")
        print(f"  MLX version: {mx.__version__ if hasattr(mx, '__version__') else 'unknown'}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import MLX: {e}")
        return False
    except Exception as e:
        print(f"✗ Error importing MLX: {e}")
        return False

def test_mlx_device():
    """Test MLX device detection"""
    try:
        import mlx.core as mx
        device = mx.default_device()
        print(f"✓ MLX default device: {device}")
        return True
    except Exception as e:
        print(f"✗ Error detecting MLX device: {e}")
        return False

def test_torch_mps():
    """Test PyTorch MPS support"""
    try:
        import torch
        if torch.backends.mps.is_available():
            print("✓ PyTorch MPS is available")
            print(f"  MPS device count: {torch.mps.device_count()}")
            return True
        else:
            print("⚠ PyTorch MPS is not available")
            return False
    except Exception as e:
        print(f"✗ Error testing PyTorch MPS: {e}")
        return False

def main():
    """Run all tests"""
    print("Running Apple Silicon MLX tests...")
    print("================================")
    
    tests = [
        test_mlx_import,
        test_mlx_device,
        test_torch_mps
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
    
    print("\nResults: {}/{} tests passed".format(passed, total))
    
    if passed == total:
        print("All tests passed! MLX is ready for Apple Silicon optimization.")
        return 0
    else:
        print("Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
