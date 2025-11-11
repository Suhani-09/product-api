
# --- 1. PROVISION THE POSTGRES INSTANCE WITH BOTH PUBLIC AND PRIVATE IP ---
resource "google_sql_database_instance" "primary" {
  provider = google
  name     = "product-api-db-instance"
  region   = "asia-south1"
  database_version = "POSTGRES_14"

  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled    = true # Enable public IP
      authorized_networks {
        name  = "allow-all"
        value = "0.0.0.0/0" # Allow all IPs for testing (not secure for prod)
      }
      # Uncomment below to also enable private IP (optional, for GKE private networking)
      # private_network = "projects/oceanic-spot-477008-k6/global/networks/default"
    }
  }
  deletion_protection = false
}

# --- 2. CREATE THE DATABASE USER ---
resource "google_sql_user" "default_user" {
  provider = google
  name     = "postgres"
  instance = google_sql_database_instance.primary.name
  password = "Kirti#13" # 👈 Set your password
}

# --- 3. OUTPUTS ---
output "db_instance_connection_name" {
  value = google_sql_database_instance.primary.connection_name
  description = "The connection name for the Cloud SQL instance."
}