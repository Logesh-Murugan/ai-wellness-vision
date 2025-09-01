#!/bin/bash

# AI Wellness Vision Deployment Script
set -e

# Configuration
NAMESPACE=${NAMESPACE:-ai-wellness-vision}
IMAGE_TAG=${IMAGE_TAG:-latest}
ENVIRONMENT=${ENVIRONMENT:-production}

echo "🚀 Starting deployment of AI Wellness Vision..."
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"
echo "Image Tag: $IMAGE_TAG"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if we can connect to the cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi

# Create namespace if it doesn't exist
echo "📦 Creating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply configurations
echo "⚙️ Applying configurations..."
kubectl apply -f k8s/secrets.yaml -n $NAMESPACE
kubectl apply -f k8s/configmap.yaml -n $NAMESPACE
kubectl apply -f k8s/persistent-volumes.yaml -n $NAMESPACE
kubectl apply -f k8s/postgres.yaml -n $NAMESPACE
kubectl apply -f k8s/redis.yaml -n $NAMESPACE
kubectl apply -f k8s/monitoring-config.yaml -n $NAMESPACE
kubectl apply -f k8s/monitoring.yaml -n $NAMESPACE

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s

# Update image tags in deployment
echo "🏗️ Updating application deployment..."
kubectl apply -f k8s/ai-wellness-app.yaml -n $NAMESPACE
kubectl apply -f k8s/hpa.yaml -n $NAMESPACE
kubectl apply -f k8s/network-policies.yaml -n $NAMESPACE

# Wait for deployments to be ready
echo "⏳ Waiting for application deployments..."
kubectl wait --for=condition=available deployment/ai-wellness-api -n $NAMESPACE --timeout=600s
kubectl wait --for=condition=available deployment/ai-wellness-streamlit -n $NAMESPACE --timeout=600s
kubectl wait --for=condition=available deployment/ai-wellness-worker -n $NAMESPACE --timeout=600s

# Wait for monitoring deployments
echo "⏳ Waiting for monitoring deployments..."
kubectl wait --for=condition=available deployment/prometheus -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=available deployment/grafana -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=available deployment/alertmanager -n $NAMESPACE --timeout=300s

# Run health checks
echo "🏥 Running health checks..."
kubectl run health-check --image=curlimages/curl:latest --rm -i --restart=Never -n $NAMESPACE -- \
    curl -f http://ai-wellness-api-service:8000/health

# Check monitoring endpoints
echo "📊 Checking monitoring endpoints..."
kubectl run prometheus-check --image=curlimages/curl:latest --rm -i --restart=Never -n $NAMESPACE -- \
    curl -f http://prometheus-service:9090/-/healthy

kubectl run grafana-check --image=curlimages/curl:latest --rm -i --restart=Never -n $NAMESPACE -- \
    curl -f http://grafana-service:3000/api/health

# Check deployment status
echo "📊 Deployment status:"
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

echo "✅ Deployment completed successfully!"

# Optional: Run smoke tests
if [ "$RUN_SMOKE_TESTS" = "true" ]; then
    echo "🧪 Running smoke tests..."
    kubectl run smoke-test --image=ai-wellness-vision:$IMAGE_TAG --rm -i --restart=Never -n $NAMESPACE -- \
        python -m pytest tests/test_smoke.py -v
fi

echo "🎉 AI Wellness Vision is now deployed and running!"