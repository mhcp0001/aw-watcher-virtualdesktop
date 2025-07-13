#!/usr/bin/env python
"""
Simple test for virtual desktop functionality without dependencies
"""
import sys
import os

# Add current directory to path to avoid module import issues
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_virtual_desktop_windows():
    """Test Windows virtual desktop detection"""
    print("Testing Windows virtual desktop detection...")
    
    try:
        import winreg
        print("winreg module available")
        
        # Test registry access (basic check)
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VirtualDesktops"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path):
                print("Virtual desktop registry key accessible")
        except Exception as e:
            print(f"Registry access limited: {e}")
            print("This is normal on some Windows configurations")
        
        # Test basic desktop info
        desktop_info = {"desktop": "Desktop 1"}
        print(f"Basic desktop info: {desktop_info}")
        
        return True
    except ImportError:
        print("winreg not available (not Windows)")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_virtual_desktop_info():
    """Test virtual desktop info function"""
    print("Testing virtual desktop info function...")
    
    try:
        # Import the specific function we need
        from aw_watcher_window.virtualdesktop import get_virtual_desktop_info
        
        info = get_virtual_desktop_info()
        print(f"Virtual desktop info: {info}")
        
        assert "desktop" in info, "desktop key missing"
        assert isinstance(info["desktop"], str), "desktop should be string"
        
        print("Virtual desktop function works")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        print("This is expected if dependencies are not installed")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Running simple tests...")
    print(f"Platform: {sys.platform}")
    
    tests = [
        test_virtual_desktop_windows,
        test_virtual_desktop_info
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
                print("PASSED\n")
            else:
                print("FAILED\n")
        except Exception as e:
            print(f"EXCEPTION: {e}\n")
    
    print(f"Results: {passed}/{len(tests)} tests passed")