# AI Wellness Vision - Deployment Guide

This guide covers the deployment of the AI Wellness Vision system using Docker and Kubernetes.

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Kubernetes 1.24+
- kubectl configured
- Helm 3.0+ (optional)

### Local Development

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Access the application
# Streamlit UI: http://localhost:8501
# API Gateway: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Production Deployment

```bash
# Build and push image
./scripts/build.sh
export PUSH_IMAGE=true
./scripts/build.sh

# Deploy to Kubernetes
./scripts/deploy.sh
```

## 📦 Docker Deployment

### Building Images

```bash
# Production build
docker build --target production -t ai-wellness-vision:latest .

# Development build
docker build --target development -t ai-wellness-vision:dev .
```

### Docker Compose

#### Development Environment
```bash
docker-compose -f docker-compose.dev.yml up -d
```

#### Production Environment
```bash
docker-compose up -d
```

## ☸️ Kubernetes Deployment

### Manual Deployment

1. **Create namespace:**
```bash
kubectl apply -f k8s/namespace.yaml
```

2. **Apply configurations:**
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/ai-wellness-app.yaml
```

3. **Verify deployment:**
```bash
kubectl get pods -n ai-wellness-vision
kubectl get services -n ai-wellness-vision
```

### Automated Deployment

Use the deployment script:
```bash
# Set environment variables
export NAMESPACE=ai-wellness-vision
export IMAGE_TAG=v1.0.0
export ENVIRONMENT=production

# Run deployment
./scripts/deploy.sh
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `SECRET_KEY` | Application secret key | - |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_WORKERS` | Number of worker processes | `4` |

### Secrets Management

Create Kubernetes secrets:
```bash
kubectl create secret generic ai-wellness-secrets \
  --from-literal=DATABASE_PASSWORD=your-password \
  --from-literal=SECRET_KEY=your-secret-key \
  -n ai-wellness-vision
```

## 🔍 Monitoring

### Prometheus Metrics

The application exposes metrics at `/metrics` endpoint:
- HTTP request metrics
- Database connection metrics
- AI model performance metrics
- System resource metrics

### Grafana Dashboard

Import the dashboard from `monitoring/grafana/dashboards/ai-wellness-dashboard.json`

### Health Checks

- **Liveness probe:** `/health`
- **Readiness probe:** `/ready`
- **Database health:** `/health/database`
- **Redis health:** `/health/redis`

## 🚨 Alerting

### Alert Rules

Key alerts configured in `monitoring/alert_rules.yml`:
- Application down
- High response time
- High error rate
- Database connectivity issues
- High resource usage

### Notification Channels

Configure notification channels in Alertmanager:
- Slack
- Email
- PagerDuty

## 🔒 Security

### SSL/TLS Configuration

1. **Generate certificates:**
```bash
# Self-signed for development
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

2. **Production certificates:**
Use Let's Encrypt with cert-manager:
```bash
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.12.0/cert-manager.yaml
```

### Security Headers

Nginx is configured with security headers:
- HSTS
- CSP
- X-Frame-Options
- X-Content-Type-Options

### Rate Limiting

- API endpoints: 10 requests/second
- Application: 5 requests/second

## 📊 Performance

### Resource Requirements

#### Minimum Requirements
- CPU: 2 cores
- Memory: 4GB RAM
- Storage: 20GB

#### Recommended for Production
- CPU: 4 cores
- Memory: 8GB RAM
- Storage: 100GB SSD

### Scaling

#### Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-wellness-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-wellness-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 🧪 Testing

### Deployment Tests

```bash
# Run deployment tests
python -m pytest tests/test_deployment.py -v

# Run smoke tests
python -m pytest tests/test_smoke.py -v
```

### Load Testing

```bash
# Install k6
curl https://github.com/grafana/k6/releases/download/v0.45.0/k6-v0.45.0-linux-amd64.tar.gz -L | tar xvz --strip-components 1

# Run load test
k6 run tests/load-test.js
```

## 🔄 CI/CD Pipeline

### GitHub Actions

The CI/CD pipeline includes:
1. **Test stage:** Unit tests, integration tests, security scans
2. **Build stage:** Docker image build and push
3. **Security stage:** Vulnerability scanning
4. **Deploy stage:** Automated deployment to staging/production

### Pipeline Configuration

See `.github/workflows/ci-cd.yml` for complete configuration.

## 🐛 Troubleshooting

### Common Issues

#### Pod Startup Issues
```bash
# Check pod logs
kubectl logs -f deployment/ai-wellness-app -n ai-wellness-vision

# Check pod events
kubectl describe pod <pod-name> -n ai-wellness-vision
```

#### Database Connection Issues
```bash
# Test database connectivity
kubectl run db-test --image=postgres:15-alpine --rm -it --restart=Never -n ai-wellness-vision -- \
  psql -h postgres-service -U postgres -d ai_wellness -c "SELECT 1;"
```

#### Performance Issues
```bash
# Check resource usage
kubectl top pods -n ai-wellness-vision
kubectl top nodes
```

### Debugging Commands

```bash
# Port forward for local debugging
kubectl port-forward service/ai-wellness-service 8000:8000 -n ai-wellness-vision

# Execute commands in pod
kubectl exec -it deployment/ai-wellness-app -n ai-wellness-vision -- /bin/bash

# View application logs
kubectl logs -f deployment/ai-wellness-app -n ai-wellness-vision --tail=100
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/docs/)

## 🆘 Support

For deployment issues:
1. Check the troubleshooting section
2. Review application logs
3. Check monitoring dashboards
4. Contact the development team

---

**Note:** This deployment guide assumes a basic understanding of Docker and Kubernetes. For production deployments, ensure proper security reviews and testing procedures are followed.