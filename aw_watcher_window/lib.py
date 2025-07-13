import sys
from typing import Optional

from .exceptions import FatalError
from .virtualdesktop import get_virtual_desktop_info


def get_current_window_linux() -> Optional[dict]:
    from . import xlib

    window = xlib.get_current_window()

    if window is None:
        cls = "unknown"
        name = "unknown"
    else:
        cls = xlib.get_window_class(window)
        name = xlib.get_window_name(window)

    window_info = {"app": cls, "title": name}
    # Add virtual desktop info
    desktop_info = get_virtual_desktop_info()
    window_info.update(desktop_info)
    
    return window_info


def get_current_window_macos(strategy: str) -> Optional[dict]:
    # TODO should we use unknown when the title is blank like the other platforms?

    # `jxa` is the default & preferred strategy. It includes the url + incognito status
    if strategy == "jxa":
        from . import macos_jxa

        window_info = macos_jxa.getInfo()
    elif strategy == "applescript":
        from . import macos_applescript

        window_info = macos_applescript.getInfo()
    else:
        raise FatalError(f"invalid strategy '{strategy}'")
    
    # Add virtual desktop info
    if window_info:
        desktop_info = get_virtual_desktop_info()
        window_info.update(desktop_info)
    
    return window_info


def get_current_window_windows() -> Optional[dict]:
    from . import windows

    window_handle = windows.get_active_window_handle()
    try:
        app = windows.get_app_name(window_handle)
    except Exception:  # TODO: narrow down the exception
        # try with wmi method
        app = windows.get_app_name_wmi(window_handle)

    title = windows.get_window_title(window_handle)

    if app is None:
        app = "unknown"
    if title is None:
        title = "unknown"

    window_info = {"app": app, "title": title}
    # Add virtual desktop info
    desktop_info = get_virtual_desktop_info()
    window_info.update(desktop_info)
    
    return window_info


def get_current_window(strategy: Optional[str] = None) -> Optional[dict]:
    """
    :raises FatalError: if a fatal error occurs (e.g. unsupported platform, X server closed)
    """

    if sys.platform.startswith("linux"):
        return get_current_window_linux()
    elif sys.platform == "darwin":
        if strategy is None:
            raise FatalError("macOS strategy not specified")
        return get_current_window_macos(strategy)
    elif sys.platform in ["win32", "cygwin"]:
        return get_current_window_windows()
    else:
        raise FatalError(f"Unknown platform: {sys.platform}")
