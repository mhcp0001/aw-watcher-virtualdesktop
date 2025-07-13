aw-watcher-virtualdesktop
=========================

Cross-platform window and virtual desktop watcher for Linux (X11), macOS, Windows.

This is an enhanced version of aw-watcher-window that also tracks virtual desktop/workspace information, allowing you to better categorize your activities by the virtual desktop you're working on.

[![Build Status](https://travis-ci.org/ActivityWatch/aw-watcher-window.svg?branch=master)](https://travis-ci.org/ActivityWatch/aw-watcher-window)

## How to install

To install the pre-built application, go to https://activitywatch.net/downloads/

To build your own packaged application, run `make package`

To install the latest git version directly from github without cloning, run
`pip install git+https://github.com/ActivityWatch/aw-watcher-window.git`

To install from a cloned version, cd into the directory and run
`poetry install` to install inside an virtualenv. You can run the binary via `aw-watcher-window`.

If you want to install it system-wide it can be installed with `pip install .`, but that has the issue
that it might not get the exact version of the dependencies due to not reading the poetry.lock file.

## Features

- Tracks active window title and application name
- **NEW: Tracks virtual desktop/workspace name**
- Supports custom virtual desktop names on Windows 10/11
- Automatically detects workspace names on Linux (X11)
- Works with macOS Spaces (requires yabai for custom names)

## Usage

In order for this watcher to be available in the UI, you'll need to have a Away From Computer (afk) watcher running alongside it.

### Virtual Desktop Tracking

The watcher now includes virtual desktop information in the activity data:

```json
{
  "app": "chrome.exe",
  "title": "GitHub - ActivityWatch",
  "desktop": "Aプロジェクト"
}
```

This allows you to:
- Name your virtual desktops according to projects (e.g., "Project A", "Research", "Personal")
- Better categorize activities even when using similar applications
- Analyze time spent per project/context based on virtual desktop usage

## Testing

### Running Tests Locally

1. **Prerequisites**:
   - Docker (for ActivityWatch server)
   - Poetry (for dependency management)

2. **Quick Test**:
   ```bash
   # Basic functionality test
   python test_simple.py
   ```

3. **Full Integration Test**:
   ```bash
   # Run complete test suite with ActivityWatch server
   ./run_tests_local.sh
   ```

4. **Docker Compose Test**:
   ```bash
   # Run tests in isolated Docker environment
   docker-compose -f docker-compose.test.yml up --build
   ```

### Continuous Integration

The project uses GitHub Actions for automated testing:
- Sets up ActivityWatch server as a service container
- Runs virtual desktop detection tests
- Performs integration tests with real ActivityWatch instance
- Simulates watcher behavior and data submission

### Note to macOS users

To log current window title the terminal needs access to macOS accessibility API.
This can be enabled in `System Preferences > Security & Privacy > Accessibility`, then add the Terminal to this list. If this is not enabled the watcher can only log current application, and not window title.

