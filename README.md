# Cloud-Native Images Gallery (Docker & Kubernetes)

![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

A full-stack, cloud-native image gallery application built with React and Flask, containerized with Docker, and deployed on Kubernetes (ArvanCloud CaaS) with high availability, persistent storage, and caching.

---

## 🏗️ Architecture & Technology Stack

* **Frontend**: React (Vite) served via Nginx in a Multi-stage Docker build. Handles SPA routing, image search, saving, and downloading.
* **Backend**: Python Flask API running on Gunicorn (4 workers, 2 threads) with SQLAlchemy ORM and custom health checks (`/health`).
* **Database**: PostgreSQL with a 5GB Persistent Volume Claim (PVC) for long-term state persistence.
* **Cache**: Redis instance caching external API responses (Openverse API) with a 300-second TTL to improve latency and reduce external call limits.
* **Orchestration**: Kubernetes manifests including Ingress routing, Secret management, Liveness/Readiness probes, Node Affinity rules, and Resource limits/requests.

---

## 📁 Repository Structure

```text
Images-gallery/
├── Backend/
│   ├── app.py              # Flask API routes (/api/search, /api/save, /health)
│   ├── models.py           # SQLAlchemy database schemas
│   ├── wait_for_db.py      # TCP check script to handle database startup ordering
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Non-root, slim Python runtime container
├── Frontend/
│   ├── src/                # React source files (App.jsx, App.css, main.jsx)
│   ├── nginx.conf          # Custom Nginx configuration with Gzip and security headers
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile          # Multi-stage Docker build (Node.js build -> Nginx runtime)
└── k8s/
    ├── namespace.yaml      # Kubernetes namespace definition (images-gallery)
    ├── secrets.yaml        # Base64 encrypted DB credentials and secrets
    ├── postgresql.yaml     # PostgreSQL Deployment, Service, and 5Gi PVC
    ├── db.yaml             # DB service alias
    ├── redis.yaml          # Redis Deployment and Service
    ├── backend.yaml        # Flask Backend Deployment (2 replicas) and Service
    ├── frontend.yaml       # React Frontend Deployment (2 replicas) and Service
    └── frontend-free-ingress.yaml  # Nginx Ingress Controller rules for API and UI routing
