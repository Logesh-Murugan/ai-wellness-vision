#!/bin/bash

# Deployment validation script for AI Wellness Vision System

set -e

# Configuration
NAMESPACE=${NAMESPACE:-ai-wellness-vision}
TIMEOUT=${TIMEOUT:-300}

echo "🔍 Validating AI Wellness Vision deployment..."
echo "Namespace: $NAMESPACE"
echo "Timeout: ${TIMEOUT}s"

# Function to check if a deployment is ready
check_deployment() {
    local deployment_name=$1
    echo "Checking deployment: $deployment_name"
    
    if kubectl get deployment $deployment_name -n $NAMESPACE &> /dev/null; then
        kubectl wait --for=condition=available deployment/$deployment_name -n $NAMESPACE --timeout=${TIMEOUT}s
        echo "✅ Deployment $deployment_name is ready"
    else
        echo "❌ Deployment $deployment_name not found"
        return 1
    fi
}

# Function to check if a service has endpoints
check_service_endpoints() {
    local service_name=$1
    echo "Checking service endpoints: $service_name"
    
    if kubectl get service $service_name -n $NAMESPACE &> /dev/null; then
        local endpoints=$(kubectl get endpoints $service_name -n $NAMESPACE -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null || echo "")
        if [ -n "$endpoints" ]; then
            echo "✅ Service $service_name has endpoints: $endpoints"
        else
            echo "❌ Service $service_name has no endpoints"
            return 1
        fi
    else
        echo "❌ Service $service_name not found"
        return 1
    fi
}

# Function to check pod health
check_pod_health() {
    local label_selector=$1
    local expected_count=$2
    echo "Checking pods with selector: $label_selector"
    
    local running_pods=$(kubectl get pods -l $label_selector -n $NAMESPACE --field-selector=status.phase=Running -o name 2>/dev/null | wc -l)
    
    if [ "$running_pods" -ge "$expected_count" ]; then
        echo "✅ Found $running_pods running pods (expected: $expected_count)"
    else
        echo "❌ Found $running_pods running pods (expected: $expected_count)"
        kubectl get pods -l $label_selector -n $NAMESPACE
        return 1
    fi
}

# Function to test HTTP endpoint
test_http_endpoint() {
    local service_name=$1
    local port=$2
    local path=$3
    local expected_status=${4:-200}
    
    echo "Testing HTTP endpoint: $service_name:$port$path"
    
    kubectl run curl-test-$(date +%s) --image=curlimages/curl:latest --rm -i --restart=Never -n $NAMESPACE -- \
        curl -s -o /dev/null -w "%{http_code}" http://$service_name:$port$path | grep -q $expected_status
    
    if [ $? -eq 0 ]; then
        echo "✅ HTTP endpoint $service_name:$port$path returned $expected_status"
    else
        echo "❌ HTTP endpoint $service_name:$port$path failed"
        return 1
    fi
}

# Function to check resource usage
check_resource_usage() {
    echo "Checking resource usage..."
    
    # Get resource usage for all pods
    kubectl top pods -n $NAMESPACE --no-headers 2>/dev/null | while read line; do
        pod_name=$(echo $line | awk '{print $1}')
        cpu_usage=$(echo $line | awk '{print $2}')
        memory_usage=$(echo $line | awk '{print $3}')
        echo "📊 Pod $pod_name: CPU=$cpu_usage, Memory=$memory_usage"
    done
}

# Function to check persistent volumes
check_persistent_volumes() {
    echo "Checking persistent volumes..."
    
    local pvcs=$(kubectl get pvc -n $NAMESPACE -o name 2>/dev/null || echo "")
    if [ -n "$pvcs" ]; then
        for pvc in $pvcs; do
            local pvc_name=$(basename $pvc)
            local status=$(kubectl get pvc $pvc_name -n $NAMESPACE -o jsonpath='{.status.phase}')
            if [ "$status" = "Bound" ]; then
                echo "✅ PVC $pvc_name is bound"
            else
                echo "❌ PVC $pvc_name is not bound (status: $status)"
            fi
        done
    else
        echo "ℹ️ No persistent volume claims found"
    fi
}

# Function to check network policies
check_network_policies() {
    echo "Checking network policies..."
    
    local netpols=$(kubectl get networkpolicy -n $NAMESPACE -o name 2>/dev/null || echo "")
    if [ -n "$netpols" ]; then
        for netpol in $netpols; do
            local netpol_name=$(basename $netpol)
            echo "✅ Network policy $netpol_name is configured"
        done
    else
        echo "⚠️ No network policies found"
    fi
}

# Function to check horizontal pod autoscalers
check_hpa() {
    echo "Checking horizontal pod autoscalers..."
    
    local hpas=$(kubectl get hpa -n $NAMESPACE -o name 2>/dev/null || echo "")
    if [ -n "$hpas" ]; then
        for hpa in $hpas; do
            local hpa_name=$(basename $hpa)
            local current_replicas=$(kubectl get hpa $hpa_name -n $NAMESPACE -o jsonpath='{.status.currentReplicas}')
            local desired_replicas=$(kubectl get hpa $hpa_name -n $NAMESPACE -o jsonpath='{.status.desiredReplicas}')
            echo "✅ HPA $hpa_name: current=$current_replicas, desired=$desired_replicas"
        done
    else
        echo "ℹ️ No horizontal pod autoscalers found"
    fi
}

# Main validation steps
echo "🚀 Starting deployment validation..."

# Check namespace exists
if kubectl get namespace $NAMESPACE &> /dev/null; then
    echo "✅ Namespace $NAMESPACE exists"
else
    echo "❌ Namespace $NAMESPACE does not exist"
    exit 1
fi

# Check core application deployments
echo "📦 Checking core application deployments..."
check_deployment "ai-wellness-api" || exit 1
check_deployment "ai-wellness-streamlit" || exit 1
check_deployment "ai-wellness-worker" || exit 1

# Check database deployments
echo "🗄️ Checking database deployments..."
check_deployment "postgres" || exit 1
check_deployment "redis" || exit 1

# Check monitoring deployments
echo "📊 Checking monitoring deployments..."
check_deployment "prometheus" || exit 1
check_deployment "grafana" || exit 1
check_deployment "alertmanager" || exit 1

# Check services and endpoints
echo "🌐 Checking services and endpoints..."
check_service_endpoints "ai-wellness-api-service" || exit 1
check_service_endpoints "ai-wellness-streamlit-service" || exit 1
check_service_endpoints "postgres-service" || exit 1
check_service_endpoints "redis-service" || exit 1
check_service_endpoints "prometheus-service" || exit 1
check_service_endpoints "grafana-service" || exit 1

# Check pod health
echo "🏥 Checking pod health..."
check_pod_health "app=ai-wellness-api" 1 || exit 1
check_pod_health "app=ai-wellness-streamlit" 1 || exit 1
check_pod_health "app=postgres" 1 || exit 1
check_pod_health "app=redis" 1 || exit 1

# Test HTTP endpoints
echo "🌍 Testing HTTP endpoints..."
test_http_endpoint "ai-wellness-api-service" "8000" "/health" "200" || exit 1
test_http_endpoint "ai-wellness-api-service" "8000" "/ready" "200" || exit 1
test_http_endpoint "prometheus-service" "9090" "/-/healthy" "200" || exit 1
test_http_endpoint "grafana-service" "3000" "/api/health" "200" || exit 1

# Check resource usage
check_resource_usage

# Check persistent volumes
check_persistent_volumes

# Check network policies
check_network_policies

# Check horizontal pod autoscalers
check_hpa

# Final validation
echo "🔍 Running final validation..."

# Check if all pods are ready
total_pods=$(kubectl get pods -n $NAMESPACE --no-headers | wc -l)
ready_pods=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase=Running --no-headers | wc -l)

echo "📊 Pod status: $ready_pods/$total_pods ready"

if [ "$ready_pods" -eq "$total_pods" ]; then
    echo "✅ All pods are running"
else
    echo "❌ Not all pods are running"
    kubectl get pods -n $NAMESPACE
    exit 1
fi

# Check ingress if it exists
if kubectl get ingress -n $NAMESPACE &> /dev/null; then
    echo "🌐 Ingress configuration:"
    kubectl get ingress -n $NAMESPACE
fi

echo "🎉 Deployment validation completed successfully!"
echo "📋 Summary:"
echo "  - Namespace: $NAMESPACE"
echo "  - Total pods: $total_pods"
echo "  - Ready pods: $ready_pods"
echo "  - All services have endpoints"
echo "  - All HTTP endpoints are responding"
echo "  - Monitoring stack is operational"

exit 0