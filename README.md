# Product API — Scalable REST API on Google Kubernetes Engine (GKE)

A production-ready REST API built with Flask, deployed on Google Kubernetes Engine (GKE) with CI/CD, monitoring, structured logging, and layered security.

---

## Table of Contents

* Overview
* Architecture
* Features
* Prerequisites
* Setup Overview
* API Documentation
* Monitoring and Logging
* Security
* CI/CD Pipeline
* Testing
* Troubleshooting
* Project Structure
* Technologies Used
* Cost and Optimization
* Contact

---

## Overview

This project demonstrates a cloud‑native REST API designed for scalability, reliability, and security on Google Cloud. It exposes CRUD endpoints for product data and follows DevOps best practices across build, deploy, and operate stages.

**Core Components**

* Backend: Python (Flask)
* Database: Google Cloud SQL (PostgreSQL)
* Containerization: Docker
* Orchestration: Google Kubernetes Engine (GKE)
* CI/CD: GitHub Actions
* Monitoring: Google Cloud Monitoring and Prometheus
* Logging: Google Cloud Logging (structured JSON)

---

## Architecture

```
GitHub Repository → GitHub Actions (Build, Test, Deploy)
        ↓
Google Kubernetes Engine (GKE)
        ↓
Load Balancer → Product API Pods (Flask App + Cloud SQL Auth Proxy)
        ↓
Cloud SQL (PostgreSQL)
        ↓
Google Cloud Monitoring & Logging
```

---

## Features

### Application

* CRUD operations for products
* RESTful API design
* Auto‑updating timestamps in database
* Health and metrics endpoints
* Structured JSON logging

### Security

* API key authentication (Admin and Read‑only)
* Authorization enforced for write operations (admin key required)
* Cloud SQL Auth Proxy for secure DB connectivity
* Secrets via Kubernetes Secrets and Google Secret Manager
* Workload Identity with least‑privilege IAM roles
* Request rate limiting (200/hour, 50/minute)

### Scalability and Reliability

* Minimum two replicas
* Horizontal Pod Autoscaler (2–10 pods)
* Pod Disruption Budget
* Rolling updates with zero downtime
* Liveness and readiness probes

### Monitoring and Observability

* Logs in Google Cloud Logging
* Alerts for CPU > 80%, error rate > 5%, pod restarts > 3
* Email notifications for alerts
* Prometheus metrics exposed for dashboards

---

## Prerequisites

* Google Cloud account
* Installed tools: gcloud, kubectl, docker, git
* GitHub account for CI/CD

---

## Setup Overview

1. Create a Cloud SQL (PostgreSQL) instance.
2. Create a GKE cluster with autoscaling enabled.
3. Configure service accounts and Workload Identity.
4. Store secrets in Secret Manager; surface them via Kubernetes Secrets.
5. Deploy Kubernetes manifests (deployment, service, HPA, PDB).
6. Use Cloud SQL Auth Proxy sidecar for secure DB access.
7. Initialize the database using the secured admin setup endpoint.
8. Configure Cloud Monitoring alert policies and notification channels.
9. Configure GitHub Actions with required repository secrets for CI/CD.

---

## API Documentation

**Base URL**

```
http://<LOAD_BALANCER_IP>
```

**Authentication**
Send API key in header: `X-API-Key: <YOUR_API_KEY>`

**Endpoints**

* `GET /products` — List all products (public)
* `GET /products/{id}` — Get product by id (public)
* `POST /products` — Create product (admin key)
* `PUT /products/{id}` — Update product (admin key)
* `DELETE /products/{id}` — Delete product (admin key)
* `GET /health` — Application and DB health
* `GET /metrics` — Prometheus metrics

**Error Responses**

* 401 Unauthorized — API key required
* 403 Forbidden — Invalid key or insufficient permissions
* 404 Not Found — Resource does not exist
* 429 Too Many Requests — Rate limit exceeded

---

## Monitoring and Logging

* Structured logs available in Cloud Logging.
* Prometheus metrics exposed at `/metrics` for dashboards.
* Alerting configured for CPU saturation, error spikes, and frequent restarts.
* Email notifications sent on alert thresholds.

---

## Security

* **Authorization and Authentication**: Admin key required for write endpoints; read endpoints public or protected by read‑only key.
* **Least Privilege**: GKE and CI/CD service accounts have minimal IAM roles.
* **Secret Management**: Database credentials and API keys stored in Google Secret Manager and mounted via Kubernetes Secrets.
* **Cloud SQL Auth Proxy**: Encrypted, IAM‑based connectivity to Cloud SQL; no public DB exposure, no static passwords in code.
* **Operational Controls**: Rate limiting, regular key rotation, TLS in transit, and audit‑friendly structured logs (without logging raw secrets).

---

## CI/CD Pipeline

**Triggers**: Pushes and pull requests to the main branch.

**Stages**

1. Checkout source
2. Authenticate to Google Cloud
3. Build Docker image
4. Push to Artifact Registry
5. Deploy to GKE
6. Post‑deployment health checks
7. Integration tests

---

## Testing

* Validated all CRUD endpoints with valid and invalid inputs.
* Verified admin vs read‑only key behavior.
* Confirmed database operations via Cloud SQL through the proxy.
* Observed autoscaling under load and successful rolling updates.
* Verified alert triggers for CPU, error rate, and pod restarts.

---

## Troubleshooting

| Issue                   | What to Check                                                       | Likely Resolution                                                      |
| ----------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Pods not starting       | Secrets, environment variables, resource limits, probe failures     | Fix config values, adjust resources, redeploy                          |
| Database not connecting | Cloud SQL Auth Proxy status, IAM bindings, DB instance availability | Ensure proxy sidecar runs, verify roles, confirm instance state        |
| API not reachable       | External IP from LoadBalancer, service type, readiness state        | Wait for provisioning, verify service config, check readiness/liveness |
| Authentication failing  | API key in header, secret values, key scope (admin vs read‑only)    | Rotate keys, update secrets, enforce correct header                    |
| CI/CD failing           | GitHub Actions logs, GCP credentials, Artifact Registry path        | Correct repository secrets and IAM permissions                         |

---

## Project Structure

```
product-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── models.py
│   └── auth.py
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   └── secrets.yaml
├── monitoring/
│   ├── cpu_alert.yaml
│   ├── error_rate_alert.yaml
│   └── pod_restart_alert.yaml
├── .github/workflows/
│   └── ci-cd.yml
├── tests/
│   └── integration_test.py
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Technologies Used

| Category         | Technology              |
| ---------------- | ----------------------- |
| Language         | Python 3.10             |
| Framework        | Flask                   |
| Database         | PostgreSQL (Cloud SQL)  |
| ORM              | SQLAlchemy              |
| Containerization | Docker                  |
| Orchestration    | Kubernetes (GKE)        |
| CI/CD            | GitHub Actions          |
| Monitoring       | Google Cloud Monitoring |
| Logging          | Google Cloud Logging    |
| Metrics          | Prometheus              |

---
## Contact

Author: Suhani Kheterpal
Email: [kheterpalsuhani@gmail.com]
