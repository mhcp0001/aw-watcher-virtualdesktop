#!/bin/bash
# Setup ActivityWatch server for testing

set -e

echo "Setting up ActivityWatch server for testing..."

# Check if running in CI
if [ "$CI" = "true" ]; then
    echo "Running in CI environment - using service container"
    # Wait for service container to be ready
    timeout 60 bash -c 'until curl -f http://localhost:5600/api/0/info; do echo "Waiting for ActivityWatch..."; sleep 2; done'
    echo "ActivityWatch server is ready at http://localhost:5600"
    exit 0
fi

# Local development setup
echo "Setting up ActivityWatch locally..."

# Check if ActivityWatch is already running
if curl -f http://localhost:5600/api/0/info >/dev/null 2>&1; then
    echo "ActivityWatch is already running at http://localhost:5600"
    exit 0
fi

# Check if Docker is available
if command -v docker >/dev/null 2>&1; then
    echo "Starting ActivityWatch with Docker..."
    
    # Stop any existing container
    docker stop activitywatch-test >/dev/null 2>&1 || true
    docker rm activitywatch-test >/dev/null 2>&1 || true
    
    # Start ActivityWatch container
    docker run -d \
        --name activitywatch-test \
        -p 5600:5600 \
        activitywatch/activitywatch:latest
    
    # Wait for it to be ready
    echo "Waiting for ActivityWatch to start..."
    timeout 60 bash -c 'until curl -f http://localhost:5600/api/0/info; do echo "Waiting..."; sleep 2; done'
    echo "ActivityWatch server is ready at http://localhost:5600"
    
else
    echo "Docker not found. Please install Docker or run ActivityWatch manually."
    echo "To run ActivityWatch manually:"
    echo "1. Download from https://activitywatch.net/downloads/"
    echo "2. Run the ActivityWatch application"
    echo "3. Ensure it's running on http://localhost:5600"
    exit 1
fi