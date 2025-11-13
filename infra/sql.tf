
resource "google_sql_database_instance" "primary" {
  provider = google
  name     = "product-api-db-instance"
  region   = "asia-south1"
  database_version = "POSTGRES_14"

  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled    = true 
      authorized_networks {
        name  = "allow-all"
        value = "0.0.0.0/0" 
      }
      
    }
  }
  deletion_protection = false
}


resource "google_sql_user" "default_user" {
  provider = google
  name     = "postgres"
  instance = google_sql_database_instance.primary.name
  password = "Kirti#13" 
}


output "db_instance_connection_name" {
  value = google_sql_database_instance.primary.connection_name
  description = "The connection name for the Cloud SQL instance."
}