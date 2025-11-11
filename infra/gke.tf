# ================================
# Google Kubernetes Engine (GKE)
# ================================

# -------------------------------
# GKE Cluster Definition
# -------------------------------
resource "google_container_cluster" "primary" {
  name     = "my-app-cluster"
  location = "asia-south1"

  # Use default network & subnetwork (you can change if you use custom VPC)
  network    = "default"
  subnetwork = "default"

  # Remove default node pool so we can create a custom one
  remove_default_node_pool = true
  initial_node_count       = 1

  # Enable IP allocation policy for VPC-native clusters
  ip_allocation_policy {
    cluster_secondary_range_name  = "gke-pods-range"
    services_secondary_range_name = "gke-services-range"
  }

  # Enable Workload Identity for secure GCP IAM integration
  workload_identity_config {
    workload_pool = "oceanic-spot-477008-k6.svc.id.goog"
  }

  # Optional: basic logging/monitoring
  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"

  # (Optional) Release channel for automatic version upgrades
  release_channel {
    channel = "REGULAR"
  }
}

# -------------------------------
# Node Pool Definition
# -------------------------------
resource "google_container_node_pool" "default_pool" {
  name       = "default-pool"
  cluster    = google_container_cluster.primary.name
  location   = google_container_cluster.primary.location

  # Number of nodes (1 for minimal cost)
  node_count = 1

  # Node configuration
  node_config {
    machine_type = "e2-small"   # 2 vCPU, 2 GB RAM — stable + low cost
    disk_size_gb = 20           # Give enough space for pods/system
    preemptible  = false        # Change to true if you want cheaper spot nodes

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      env = "dev"
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  # Node management — keep it healthy
  management {
    auto_repair  = true
    auto_upgrade = true
  }

  # Optional: enable autoscaling (min=1, max=2)
  autoscaling {
    min_node_count = 1
    max_node_count = 2
  }
}
