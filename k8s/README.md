# Kubernetes Deployment Steps

1. Create Namespace & Secrets
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml -n images-gallery
```
2. Deploy Database & Cache
```bash
kubectl apply -f k8s/postgresql.yaml -n images-gallery
kubectl apply -f k8s/db.yaml -n images-gallery
kubectl apply -f k8s/redis.yaml -n images-gallery

# Wait for PostgreSQL to be ready
kubectl rollout status deployment/postgresql -n images-gallery --timeout=120s
```
3. Deploy Backend & Frontend
```bash
kubectl apply -f k8s/backend.yaml -n images-gallery
kubectl apply -f k8s/frontend.yaml -n images-gallery

# Verify rollout status
kubectl rollout status deployment/backend -n images-gallery
kubectl rollout status deployment/frontend -n images-gallery
```
4. Configure Ingress Routing
```bash
kubectl apply -f k8s/frontend-free-ingress.yaml -n images-gallery
```
# Diagnostics & Health Checks
Verify pod status and resource utilization within the namespace:
```bash
# Get all running pods and services
kubectl get all -n images-gallery

# Check backend health logs
kubectl logs -f deployment/backend -n images-gallery

# Local port forwarding test
kubectl port-forward svc/backend-service 8000:8000 -n images-gallery
curl http://localhost:8000/health
```

