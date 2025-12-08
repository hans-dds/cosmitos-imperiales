#!/bin/bash

# Script to run SonarScanner using Docker
# Usage: ./scripts/run_sonar_scan.sh [SONAR_TOKEN]

# If token is provided as argument, use it. Otherwise try to use valid defaults or fail gracefully.
TOKEN=$1

if [ -z "$TOKEN" ]; then
    echo "No token provided. Running scanner without authentication token."
    echo "If project requires auth, please provide token: ./scripts/run_sonar_scan.sh <TOKEN>"
    # Note: If SonarQube has "Force user authentication" disabled, this works. 
    # Otherwise it fails.
fi

# Ensure we are in the project root (assuming script is in scripts/)
cd "$(dirname "$0")/.."

echo "Starting SonarScanner..."
PROJECT_ROOT=$(pwd)
echo "Project Root: $PROJECT_ROOT"

# Fix coverage paths for Docker
# Local paths like /home/user/project/src need to be /usr/src/src in the container
if [ -f "coverage.xml" ]; then
    echo "Adjusting coverage.xml paths for Docker..."
    sed "s|$PROJECT_ROOT|/usr/src|g" coverage.xml > coverage.docker.xml
    COVERAGE_REPORT="coverage.docker.xml"
else
    echo "Warning: coverage.xml not found. Coverage metrics might be missing."
    COVERAGE_REPORT="coverage.xml"
fi

# Use --network host to access localhost:9000 easily on Linux
docker run \
    --rm \
    --network host \
    -e SONAR_HOST_URL="http://localhost:9000" \
    -e SONAR_TOKEN="$TOKEN" \
    -e SONAR_SCANNER_OPTS="-Dsonar.projectKey=cosmitos1" \
    -v "$PROJECT_ROOT:/usr/src" \
    -v "$PROJECT_ROOT/$COVERAGE_REPORT:/usr/src/coverage.xml" \
    sonarsource/sonar-scanner-cli

# Cleanup
if [ -f "coverage.docker.xml" ]; then
    rm coverage.docker.xml
fi

echo "Scan finished."
