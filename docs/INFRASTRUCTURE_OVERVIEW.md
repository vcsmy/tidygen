# Infrastructure Directory

This directory contains all infrastructure-related configurations, deployment scripts, and environment-specific settings for the TidyGen ERP platform.

## 📁 Structure

```
infra/
├── docker/         # Docker configurations
├── k8s/           # Kubernetes manifests
├── terraform/     # Infrastructure provisioning
└── ci-cd/         # CI/CD pipeline configurations
```

## 🐳 Docker

### Development Environment
```bash
# Start development environment
docker-compose -f infra/docker/development/docker-compose.yml up -d

# View logs
docker-compose -f infra/docker/development/docker-compose.yml logs -f

# Stop environment
docker-compose -f infra/docker/development/docker-compose.yml down
```

### Production Environment
```bash
# Deploy to production
docker-compose -f infra/docker/production/docker-compose.yml up -d
```

## ☸️ Kubernetes

### Deploy to Kubernetes
```bash
# Apply all manifests
kubectl apply -f infra/k8s/

# Deploy specific components
kubectl apply -f infra/k8s/deployments/
kubectl apply -f infra/k8s/services/
kubectl apply -f infra/k8s/ingress/
```

### Helm Charts
```bash
# Install main application
helm install tidygen-erp infra/k8s/helm/tidygen-erp/

# Install monitoring stack
helm install monitoring infra/k8s/helm/monitoring/
```

## 🏗️ Terraform

### Infrastructure Provisioning
```bash
# Initialize Terraform
cd infra/terraform
terraform init

# Plan infrastructure changes
terraform plan -var-file="environments/dev/terraform.tfvars"

# Apply infrastructure
terraform apply -var-file="environments/dev/terraform.tfvars"
```

### Environments
- **Development**: `environments/dev/`
- **Staging**: `environments/staging/`
- **Production**: `environments/prod/`

## 🚀 CI/CD

### GitHub Actions
- **CI Pipeline**: `ci-cd/github-actions/ci.yml`
- **CD Pipeline**: `ci-cd/github-actions/cd.yml`
- **Security Scanning**: `ci-cd/github-actions/security.yml`

### Jenkins
- **Main Pipeline**: `ci-cd/jenkins/Jenkinsfile`
- **Pipeline Definitions**: `ci-cd/jenkins/pipelines/`

### GitLab CI
- **Pipeline Configuration**: `ci-cd/gitlab-ci/.gitlab-ci.yml`

## 🔧 Configuration Management

### Environment Variables
- **Development**: `.env.example` in each environment directory
- **Staging**: `.env.staging` with staging-specific values
- **Production**: `.env.production` with production values

### Secrets Management
- **Kubernetes**: Store secrets in `k8s/secrets/`
- **Docker**: Use Docker secrets for sensitive data
- **Terraform**: Use Terraform variables for infrastructure secrets

## 📊 Monitoring & Observability

### Monitoring Stack
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **Jaeger**: Distributed tracing
- **ELK Stack**: Log aggregation and analysis

### Health Checks
- **Application Health**: `/health` endpoint
- **Database Health**: Connection monitoring
- **External Services**: Third-party service monitoring

## 🛡️ Security

### Security Best Practices
- **Container Security**: Regular base image updates
- **Network Security**: Proper firewall rules
- **Secret Management**: Encrypted secrets storage
- **Access Control**: RBAC for Kubernetes

### Security Scanning
- **Container Scanning**: Trivy for vulnerability detection
- **Code Scanning**: SonarQube for code quality
- **Dependency Scanning**: Automated dependency updates

## 📚 Documentation

- [Docker Setup Guide](docker/README.md)
- [Kubernetes Deployment Guide](k8s/README.md)
- [Terraform Infrastructure Guide](terraform/README.md)
- [CI/CD Pipeline Documentation](ci-cd/README.md)
- [Monitoring Setup Guide](../../docs/deployment/monitoring.md)

## 🆘 Troubleshooting

### Common Issues
1. **Container Startup Issues**: Check logs with `docker-compose logs`
2. **Kubernetes Deployment Issues**: Use `kubectl describe` for detailed information
3. **Terraform State Issues**: Check state file and backend configuration
4. **CI/CD Pipeline Issues**: Review workflow logs in GitHub Actions

### Support
- **Infrastructure Issues**: Check monitoring dashboards
- **Deployment Issues**: Review CI/CD pipeline logs
- **Configuration Issues**: Validate environment variables and secrets
