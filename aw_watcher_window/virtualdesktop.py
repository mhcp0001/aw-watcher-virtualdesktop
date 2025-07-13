"""
Virtual Desktop information retrieval for different platforms
"""
import sys
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


def get_virtual_desktop_info() -> Dict[str, str]:
    """
    Get virtual desktop information for the current window.
    Returns a dictionary with 'desktop' key containing the desktop name.
    """
    desktop_info = {"desktop": "unknown"}
    
    try:
        if sys.platform == "win32":
            desktop_info = get_virtual_desktop_windows()
        elif sys.platform.startswith("linux"):
            desktop_info = get_virtual_desktop_linux()
        elif sys.platform == "darwin":
            desktop_info = get_virtual_desktop_macos()
    except Exception as e:
        logger.warning(f"Failed to get virtual desktop info: {e}")
    
    return desktop_info


def get_virtual_desktop_windows() -> Dict[str, str]:
    """Get virtual desktop name on Windows 10/11"""
    try:
        import winreg
        import win32gui
        import win32com.client
        import pythoncom
        
        # Get current desktop ID through registry
        # Windows stores virtual desktop names in registry
        desktop_name = "Desktop 1"  # Default
        
        try:
            # Initialize COM
            pythoncom.CoInitialize()
            
            # Try to get desktop name from registry
            # This is a simplified approach - full implementation would need IVirtualDesktopManager COM interface
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VirtualDesktops"
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    # Get current desktop
                    current_desktop_id, _ = winreg.QueryValueEx(key, "CurrentVirtualDesktop")
                    
                    # Try to find desktop name
                    desktops_key_path = f"{key_path}\\Desktops\\{{{current_desktop_id}}}"
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, desktops_key_path) as desktop_key:
                            name, _ = winreg.QueryValueEx(desktop_key, "Name")
                            if name:
                                desktop_name = name
                    except:
                        pass
            except Exception as e:
                logger.debug(f"Registry access failed: {e}")
                
            # Fallback: use desktop number
            # This requires more complex COM implementation
            # For now, we'll use a simplified approach
            
        finally:
            pythoncom.CoUninitialize()
            
        return {"desktop": desktop_name}
        
    except ImportError:
        logger.warning("Required Windows modules not available")
        return {"desktop": "unknown"}
    except Exception as e:
        logger.debug(f"Windows virtual desktop detection failed: {e}")
        return {"desktop": "Desktop 1"}


def get_virtual_desktop_linux() -> Dict[str, str]:
    """Get workspace name on Linux (X11)"""
    try:
        from . import xlib
        import Xlib.display
        
        display = Xlib.display.Display()
        root = display.screen().root
        
        # Get current desktop number
        current_desktop = root.get_full_property(
            display.intern_atom('_NET_CURRENT_DESKTOP'),
            Xlib.X.AnyPropertyType
        )
        
        if current_desktop:
            desktop_num = current_desktop.value[0]
            
            # Try to get desktop names
            desktop_names = root.get_full_property(
                display.intern_atom('_NET_DESKTOP_NAMES'),
                Xlib.X.AnyPropertyType
            )
            
            if desktop_names and desktop_names.value:
                # Parse null-terminated strings
                names = desktop_names.value.decode('utf-8', errors='ignore').split('\x00')
                names = [n for n in names if n]  # Remove empty strings
                
                if desktop_num < len(names) and names[desktop_num]:
                    return {"desktop": names[desktop_num]}
            
            # Fallback to desktop number
            return {"desktop": f"Desktop {desktop_num + 1}"}
        
        return {"desktop": "Desktop 1"}
        
    except Exception as e:
        logger.debug(f"Linux virtual desktop detection failed: {e}")
        return {"desktop": "unknown"}


def get_virtual_desktop_macos() -> Dict[str, str]:
    """Get space/desktop info on macOS"""
    try:
        # macOS doesn't provide easy API access to Space names
        # We can get the space number though
        import subprocess
        import json
        
        # Try to get current space info using yabai if available
        try:
            result = subprocess.run(
                ["yabai", "-m", "query", "--spaces", "--space"],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                space_info = json.loads(result.stdout)
                space_index = space_info.get("index", 1)
                space_label = space_info.get("label", f"Desktop {space_index}")
                return {"desktop": space_label}
        except:
            pass
        
        # Fallback: Use desktop number
        # This would require Accessibility permissions and CGS private APIs
        return {"desktop": "Desktop 1"}
        
    except Exception as e:
        logger.debug(f"macOS virtual desktop detection failed: {e}")
        return {"desktop": "unknown"}