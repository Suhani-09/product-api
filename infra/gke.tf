
resource "google_container_cluster" "primary" {
  name     = "my-app-cluster"
  location = "asia-south1"

  
  network    = "default"
  subnetwork = "default"

  
  remove_default_node_pool = true
  initial_node_count       = 1

  
  ip_allocation_policy {
    cluster_secondary_range_name  = "gke-pods-range"
    services_secondary_range_name = "gke-services-range"
  }

  
  workload_identity_config {
    workload_pool = "oceanic-spot-477008-k6.svc.id.goog"
  }

  
  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"

  
  release_channel {
    channel = "REGULAR"
  }
}


resource "google_container_node_pool" "default_pool" {
  name       = "default-pool"
  cluster    = google_container_cluster.primary.name
  location   = google_container_cluster.primary.location

  
  node_count = 1

  
  node_config {
    machine_type = "e2-small"   
    disk_size_gb = 20           
    preemptible  = false        

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

  
  management {
    auto_repair  = true
    auto_upgrade = true
  }

  
  autoscaling {
    min_node_count = 1
    max_node_count = 2
  }
}
