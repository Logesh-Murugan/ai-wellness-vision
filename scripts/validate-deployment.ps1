 # Deployment validation script for AI Wellness Vision System (PowerShell)

param(
    [string]$Namespace = "ai-wellness-vision",
    [int]$Timeout = 300
)

$ErrorActionPreference = "Stop"

Write-Host "🔍 Validating AI Wellness Vision deployment..." -ForegroundColor Green
Write-Host "Namespace: $Namespace" -ForegroundColor Cyan
Write-Host "Timeout: ${Timeout}s" -ForegroundColor Cyan

# Function to check if a deployment is ready
function Test-Deployment {
    param([string]$DeploymentName)
    
    Write-Host "Checking deployment: $DeploymentName" -ForegroundColor Yellow
    
    try {
        kubectl get deployment $DeploymentName -n $Namespace | Out-Null
        kubectl wait --for=condition=available deployment/$DeploymentName -n $Namespace --timeout="${Timeout}s" | Out-Null
        Write-Host "✅ Deployment $DeploymentName is ready" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Deployment $DeploymentName failed: $_" -ForegroundColor Red
        return $false
    }
}

# Function to check if a service has endpoints
function Test-ServiceEndpoints {
    param([string]$ServiceName)
    
    Write-Host "Checking service endpoints: $ServiceName" -ForegroundColor Yellow
    
    try {
        kubectl get service $ServiceName -n $Namespace | Out-Null
        $endpoints = kubectl get endpoints $ServiceName -n $Namespace -o jsonpath='{.subsets[*].addresses[*].ip}' 2>$null
        
        if ($endpoints) {
            Write-Host "✅ Service $ServiceName has endpoints: $endpoints" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "❌ Service $ServiceName has no endpoints" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Service $ServiceName not found: $_" -ForegroundColor Red
        return $false
    }
}

# Function to test HTTP endpoint
function Test-HttpEndpoint {
    param(
        [string]$ServiceName,
        [string]$Port,
        [string]$Path,
        [string]$ExpectedStatus = "200"
    )
    
    Write-Host "Testing HTTP endpoint: ${ServiceName}:${Port}${Path}" -ForegroundColor Yellow
    
    try {
        $testName = "curl-test-$(Get-Date -Format 'yyyyMMddHHmmss')"
        $result = kubectl run $testName --image=curlimages/curl:latest --rm -i --restart=Never -n $Namespace -- curl -s -o /dev/null -w "%{http_code}" "http://${ServiceName}:${Port}${Path}"
        
        if ($result -match $ExpectedStatus) {
            Write-Host "✅ HTTP endpoint ${ServiceName}:${Port}${Path} returned $ExpectedStatus" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "❌ HTTP endpoint ${ServiceName}:${Port}${Path} failed (got: $result)" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ HTTP endpoint ${ServiceName}:${Port}${Path} failed: $_" -ForegroundColor Red
        return $false
    }
}

# Function to check resource usage
function Get-ResourceUsage {
    Write-Host "Checking resource usage..." -ForegroundColor Yellow
    
    try {
        $topOutput = kubectl top pods -n $Namespace --no-headers 2>$null
        if ($topOutput) {
            foreach ($line in $topOutput) {
                $parts = $line -split '\s+'
                $podName = $parts[0]
                $cpuUsage = $parts[1]
                $memoryUsage = $parts[2]
                Write-Host "📊 Pod $podName`: CPU=$cpuUsage, Memory=$memoryUsage" -ForegroundColor Cyan
            }
        }
        else {
            Write-Host "ℹ️ Resource usage metrics not available" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠️ Could not retrieve resource usage: $_" -ForegroundColor Yellow
    }
}

# Main validation
Write-Host "🚀 Starting deployment validation..." -ForegroundColor Green

# Check namespace exists
try {
    kubectl get namespace $Namespace | Out-Null
    Write-Host "✅ Namespace $Namespace exists" -ForegroundColor Green
}
catch {
    Write-Host "❌ Namespace $Namespace does not exist" -ForegroundColor Red
    exit 1
}

$allChecksPass = $true

# Check core application deployments
Write-Host "📦 Checking core application deployments..." -ForegroundColor Magenta
$allChecksPass = $allChecksPass -and (Test-Deployment "ai-wellness-api")
$allChecksPass = $allChecksPass -and (Test-Deployment "ai-wellness-streamlit")
$allChecksPass = $allChecksPass -and (Test-Deployment "ai-wellness-worker")

# Check database deployments
Write-Host "🗄️ Checking database deployments..." -ForegroundColor Magenta
$allChecksPass = $allChecksPass -and (Test-Deployment "postgres")
$allChecksPass = $allChecksPass -and (Test-Deployment "redis")

# Check monitoring deployments
Write-Host "📊 Checking eployments..." -ForegroundColor Magenta
$allChecksPass = $allChecksPass -and (Test-Deployment "prometheus")
$allChecksPass = $allChecksPass -and (Test-Deployment "grafana")
$allChecksPass = $allChecksPass -and (Test-Deployment "alertmanager")

# Check services and endpoints
Write-Host "🌐 Checking services and endpoints..." -ForegroundColor Magenta
$allChecksPass = $allChecksPass -and (Test-ServiceEndpoints "ai-wellness-api-service")
$allChecksPass = $allChecksPass -and (Test-ServiceEndpoints "ai-wellness-streamlit-service")
$allChecksPass = $allChecksPass -and (Test-ServiceEndpoints "postgres-service")
$allChecksPass = $allChecksPass -and (Test-ServiceEndpoints "redis-service")
$allChecksPass = $allChecksPass -and (Test-ServiceEndpoints "prometheus-service")
$allChecksPass = $allChecksPass -and (Test-ServiceEndpoints "grafana-service")

# Test HTTP endpoints
Write-Host "🌍 Testing HTTP endpoints..." -ForegroundColor Magenta
$allChecksPass = $allChecksPass -and (Test-HttpEndpoint "ai-wellness-api-service" "8000" "/health" "200")
$allChecksPass = $allChecksPass -and (Test-HttpEndpoint "ai-wellness-api-service" "8000" "/