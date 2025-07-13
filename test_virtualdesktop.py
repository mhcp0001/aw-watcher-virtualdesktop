#!/usr/bin/env python
"""
Test script for virtual desktop functionality
"""
import sys
import logging
from aw_watcher_window.virtualdesktop import get_virtual_desktop_info
from aw_watcher_window.lib import get_current_window

logging.basicConfig(level=logging.DEBUG)

def test_virtual_desktop():
    print("Testing virtual desktop info retrieval...")
    print(f"Platform: {sys.platform}")
    
    # Test virtual desktop info
    desktop_info = get_virtual_desktop_info()
    print(f"Virtual Desktop Info: {desktop_info}")
    
    # Test full window info including desktop
    try:
        if sys.platform == "darwin":
            window_info = get_current_window(strategy="jxa")
        else:
            window_info = get_current_window()
        print(f"Full Window Info: {window_info}")
    except Exception as e:
        print(f"Error getting window info: {e}")

if __name__ == "__main__":
    test_virtual_desktop()