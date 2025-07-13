#!/bin/bash
# Local testing script for aw-watcher-virtualdesktop

set -e

echo "🚀 Starting local tests for aw-watcher-virtualdesktop"

# Make scripts executable
chmod +x scripts/setup_activitywatch.sh
chmod +x scripts/cleanup_activitywatch.sh

# Cleanup any previous test environment
echo "🧹 Cleaning up previous test environment..."
./scripts/cleanup_activitywatch.sh

# Setup ActivityWatch server
echo "⚙️  Setting up ActivityWatch server..."
./scripts/setup_activitywatch.sh

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

echo "🧪 Running tests..."

# Test 1: Basic virtual desktop detection
echo "Test 1: Virtual desktop detection"
poetry run python -c "
from aw_watcher_window.virtualdesktop import get_virtual_desktop_info
info = get_virtual_desktop_info()
print('✓ Virtual desktop info:', info)
assert 'desktop' in info
print('✅ Virtual desktop detection works')
"

# Test 2: ActivityWatch connection
echo "Test 2: ActivityWatch connection"
poetry run python -c "
from aw_client import ActivityWatchClient
client = ActivityWatchClient('test-local', host='localhost', port=5600, testing=True)
info = client.get_info()
print('✓ ActivityWatch info:', info)
print('✅ ActivityWatch connection works')
"

# Test 3: Integration tests
echo "Test 3: Integration tests"
poetry run python tests/test_integration.py

# Test 4: Watcher simulation
echo "Test 4: Watcher simulation"
poetry run python tests/test_watcher_simulation.py

echo "🎉 All local tests completed successfully!"

# Optional: Keep server running for manual testing
read -p "Keep ActivityWatch server running for manual testing? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Cleaning up test environment..."
    ./scripts/cleanup_activitywatch.sh
    echo "✅ Cleanup complete"
else
    echo "🔄 ActivityWatch server is still running at http://localhost:5600"
    echo "   Run './scripts/cleanup_activitywatch.sh' when done"
fi