#!/bin/bash

# AI Wellness Vision Build Script
set -e

# Configuration
IMAGE_NAME=${IMAGE_NAME:-ai-wellness-vision}
IMAGE_TAG=${IMAGE_TAG:-latest}
REGISTRY=${REGISTRY:-ghcr.io}
BUILD_TARGET=${BUILD_TARGET:-production}

echo "🏗️ Building AI Wellness Vision Docker image..."
echo "Image: $REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
echo "Target: $BUILD_TARGET"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Build the Docker image
echo "📦 Building Docker image..."
docker build \
    --target $BUILD_TARGET \
    --tag $REGISTRY/$IMAGE_NAME:$IMAGE_TAG \
    --tag $REGISTRY/$IMAGE_NAME:latest \
    .

# Run security scan if trivy is available
if command -v trivy &> /dev/null; then
    echo "🔒 Running security scan..."
    trivy image --exit-code 1 --severity HIGH,CRITICAL $REGISTRY/$IMAGE_NAME:$IMAGE_TAG
fi

# Push to registry if specified
if [ "$PUSH_IMAGE" = "true" ]; then
    echo "📤 Pushing image to registry..."
    docker push $REGISTRY/$IMAGE_NAME:$IMAGE_TAG
    docker push $REGISTRY/$IMAGE_NAME:latest
fi

echo "✅ Build completed successfully!"
echo "Image: $REGISTRY/$IMAGE_NAME:$IMAGE_TAG"