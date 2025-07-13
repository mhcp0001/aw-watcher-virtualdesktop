#!/bin/bash
# Cleanup ActivityWatch test environment

echo "Cleaning up ActivityWatch test environment..."

# Stop and remove Docker container if it exists
if command -v docker >/dev/null 2>&1; then
    docker stop activitywatch-test >/dev/null 2>&1 || true
    docker rm activitywatch-test >/dev/null 2>&1 || true
    echo "Stopped ActivityWatch test container"
fi

echo "Cleanup complete"