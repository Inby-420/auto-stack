🚀 Auto-Stack

Auto-Stack is a complete, end-to-end cloud-native DevOps project. It demonstrates a fully automated, observable, and resilient microservice application running on Kubernetes, all managed by a closed-loop GitOps pipeline.

This project goes beyond a simple "Hello, World!" to simulate the real-world challenges of a modern DevOps/SRE environment, including application monitoring, CI/CD, and configuration management.

🏗️ Core Architecture

This project is built on a monorepo and is managed entirely by GitOps. The Git repository is the single source of truth for all application code, Kubernetes manifests, and CI/CD configurations.

The entire workflow is automated:

Code Push: A developer pushes a code change to one of the application folders (e.g., worker-node/).

CI (GitHub Actions): The push triggers a GitHub Actions workflow that automatically:

Builds a new versioned Docker image for the changed application.

Pushes the new image to GitHub Container Registry (GHCR).

Reads the current version from the K8s manifest (e.g., v0.4).

Increments the version (e.g., to v0.5).

Commits the updated manifest (e.g., worker-deployment.yaml) back to the Git repo.

CD (Argo CD):

Argo CD, running in the cluster, detects the new commit to the k8s-manifests path.

It sees the cluster state is "OutOfSync" with the Git repo.

With Self Heal enabled, it automatically pulls the new v0.5 image from GHCR and triggers a rolling deployment of the updated application.

The developer's code change is now live in production with zero manual intervention.

✨ Key Features

Microservice Architecture: A 3-tier application:

traffic-sender: A load generator that sends math problems at a configurable TPS.

worker-node: A Python (FastAPI) app that solves the problems and stores them in a database.

result-node: A Python (FastAPI + Jinja2) web app that displays the results.

Kubernetes Orchestration: All applications run as Deployments on a K3s cluster.

Stateful Persistence: A PostgreSQL database runs as a StatefulSet with a PersistentVolumeClaim to store all calculation results.

Full Observability Stack:

Prometheus: Deployed via Helm, it scrapes metrics from all cluster nodes, pods, and applications.

Grafana: Provides a complete dashboard showing host health and custom application metrics.

Custom Application Metrics:

The traffic-sender exposes a Prometheus Gauge (traffic_sender_tps) for Live TPS.

The worker-node exposes a Prometheus Histogram (worker_calculation_duration_seconds) for P95 Latency.

GitOps CI/CD Pipeline:

CI: GitHub Actions for automated building, testing, and pushing of container images.

CD: Argo CD for automated, pull-based deployment from Git.

Registry: GitHub Container Registry (GHCR) for hosting private container images.

Ingress & Network Management: Uses Traefik Ingress to professionally expose services (like Grafana and the result-node) to the user.

🛠️ Technology Stack


Orchestration: Kubernetes (K3s)

Containerization: Docker

CI/CD: GitHub Actions, Argo CD, Helm

Registry: GitHub Container Registry (GHCR)

Observability: Prometheus, Grafana

Services: Python (FastAPI), PostgreSQL

Networking: Traefik

🔮 Phase 2: Future Plans

The next phase of this project is to move from observability to resiliency.

Chaos Engineering: Introduce a chaos agent (like kube-monkey) to randomly delete application pods.

Prove Self-Healing: Use the Grafana dashboard to visually demonstrate the system's resilience. We will watch the TPS and latency graphs dip during a chaos event and then automatically recover as Kubernetes's self-healing mechanisms (ReplicaSets) bring new pods online.
