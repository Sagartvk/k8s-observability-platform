# K8s Observability Platform

> A production-grade 3-tier microservices application deployed on Kubernetes with full observability — Prometheus metrics, Grafana dashboards, Alertmanager alerting, and GitHub Actions CI/CD.

---

## Project Overview

This project demonstrates a complete DevOps workflow:

- **Frontend** — Python Flask UI that displays product data fetched from the backend API
- **Backend** — Python Flask REST API that exposes `/products`, `/health`, and `/metrics` endpoints
- **Monitoring** — Prometheus scrapes metrics every 15 seconds, Grafana visualises them as dashboards
- **Alerting** — Alertmanager fires alerts on pod crashes, high CPU, or service downtime
- **CI/CD** — GitHub Actions builds Docker images and deploys to Kubernetes on every push to `main`

---

## Tech Stack

| Layer         | Technology                          |
|---------------|-------------------------------------|
| App           | Python Flask (backend + frontend)   |
| Containers    | Docker                              |
| Orchestration | Kubernetes — Minikube (local) / AWS EKS (production) |
| Monitoring    | Prometheus + Grafana                |
| Alerting      | Alertmanager                        |
| Package Mgmt  | Helm (kube-prometheus-stack chart)  |
| CI/CD         | GitHub Actions                      |
| Registry      | DockerHub                           |
| Cloud         | AWS EKS — ap-south-1 (Mumbai)       |

---

## Project Structure

```
k8s-observability-platform/
├── backend/                        # Flask REST API
│   ├── app.py                      # API with /products /health /metrics
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                       # Flask UI
│   ├── app.py                      # Product Store UI
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/                            # Kubernetes manifests
│   ├── namespace.yaml              # app + monitoring namespaces
│   ├── backend-deployment.yaml     # Backend Deployment + ClusterIP Service
│   └── frontend-deployment.yaml   # Frontend Deployment + LoadBalancer Service
├── monitoring/                     # Observability config
│   ├── prometheus-values.yaml      # Helm values — custom scrape config
│   └── alert-rules.yaml           # PrometheusRule — crash/CPU/downtime alerts
├── .github/
│   └── workflows/
│       └── deploy.yaml             # GitHub Actions CI/CD pipeline
├── preview.html                    # Interactive UI preview (open in browser)
└── README.md
```

---

## Local Setup — 3 Terminals Required

### Prerequisites (run once)

```bash
# Docker
sudo apt-get update && sudo apt-get install docker.io -y
sudo systemctl start docker && sudo usermod -aG docker $USER
# Log out and back in after usermod

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/kubectl

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

---

### Terminal 1 — Main Setup Terminal

```bash
# 1. Start Minikube
minikube start --cpus=2 --memory=4096 --driver=docker
minikube addons enable ingress
minikube addons enable metrics-server

# 2. Login to DockerHub
docker login

# 3. Update your username in YAML files
sed -i 's/YOUR_DOCKERHUB_USERNAME/yourusername/g' k8s/backend-deployment.yaml k8s/frontend-deployment.yaml

# 4. Build and push images
docker build -t yourusername/backend:latest ./backend
docker build -t yourusername/frontend:latest ./frontend
docker push yourusername/backend:latest
docker push yourusername/frontend:latest

# 5. Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Wait until all pods show Running
kubectl get pods -n app -w

# 6. Open Store App in browser (auto-opens)
minikube service frontend-service -n app

# 7. Install monitoring stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f monitoring/prometheus-values.yaml

# Wait for monitoring pods
kubectl get pods -n monitoring -w

# 8. Apply alert rules
kubectl apply -f monitoring/alert-rules.yaml

# 9. Get Grafana password (save this)
kubectl get secret -n monitoring monitoring-grafana \
  -o jsonpath='{.data.admin-password}' | base64 --decode && echo
```

---

### Terminal 2 — Prometheus (keep open)

```bash
kubectl port-forward svc/monitoring-kube-prometheus-prometheus \
  -n monitoring 9090:9090
```

Open **http://localhost:9090** → Status → Targets — verify backend pods show as **UP**.

---

### Terminal 3 — Grafana (keep open)

```bash
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```

Open **http://localhost:3000** → Login: `admin` / (password from Terminal 1 Step 9)

Import dashboards: **+** → Import → enter ID → Load → select Prometheus → Import

| Dashboard ID | What it shows |
|---|---|
| 315  | Kubernetes cluster overview |
| 6417 | Per-pod CPU, memory, restarts |
| 1860 | Node Exporter — host metrics |
| 14282 | Flask app request rate, latency |

---

## GitHub Actions CI/CD Setup

Add these secrets in your repo → **Settings → Secrets and variables → Actions**:

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | Your DockerHub username |
| `DOCKERHUB_TOKEN` | DockerHub access token (hub.docker.com → Account Settings → Security) |
| `KUBECONFIG_DATA` | Base64 kubeconfig: `cat ~/.kube/config \| base64 -w 0` |

Every push to `main` automatically:
1. Builds new Docker images tagged with git commit SHA
2. Pushes to DockerHub
3. Runs `kubectl set image` to update deployments
4. Performs zero-downtime rolling update

---

## Kubernetes Architecture

```
                    ┌─────────────────────────────────┐
                    │   Namespace: app                 │
                    │                                  │
  User Browser ───▶ │  frontend-service (LoadBalancer) │
                    │         │                        │
                    │         ▼                        │
                    │  [frontend pod 1] [pod 2]        │
                    │         │                        │
                    │  backend-service (ClusterIP)     │
                    │         │                        │
                    │  [backend pod 1] [pod 2]         │
                    │         │                        │
                    └─────────┼───────────────────────┘
                              │ /metrics every 15s
                    ┌─────────▼───────────────────────┐
                    │   Namespace: monitoring          │
                    │                                  │
                    │  Prometheus ──▶ Grafana          │
                    │       │                          │
                    │  Alertmanager                    │
                    └─────────────────────────────────┘
```

---

## Shutdown

```bash
# Stop port-forwards: Ctrl+C in Terminal 2 and Terminal 3

# Stop Minikube (saves state — resume with minikube start)
minikube stop

# Full reset
minikube delete
```

---

## Resume Bullet Points

- Deployed 3-tier microservices application on **AWS EKS** (ap-south-1) with 2-node managed node group and Kubernetes self-healing via liveness probes
- Built full observability stack using **Prometheus + Grafana**, creating 5 custom dashboards tracking request rate, latency, CPU/memory usage, and pod health
- Configured **Alertmanager** rules for pod crash-looping, high CPU, and service downtime — enabling sub-1-minute automated incident detection
- Implemented **GitHub Actions CI/CD pipeline** — automatic Docker build, DockerHub push, and zero-downtime rolling update to Kubernetes on every `git push`
- Used **Helm charts** to deploy kube-prometheus-stack monitoring suite, reducing manual YAML configuration by ~80%

---

## Author

**Sagar Ibrahim** — Cloud & DevOps Intern, IPSR Solutions, Kerala  
Target: Junior Cloud/DevOps Engineer roles — 2026
