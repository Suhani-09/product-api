resource "google_sql_database_instance" "primary" {
  provider         = google
  name             = "product-api-db-instance"
  region           = "asia-south1"
  database_version = "POSTGRES_14"

  settings {
    tier = "db-f1-micro"
    
    ip_configuration {
      ipv4_enabled = true
      ssl_mode     = "ALLOW_UNENCRYPTED_AND_ENCRYPTED" 
    }
    
    
    backup_configuration {
      enabled            = true
      start_time         = "03:00"
      point_in_time_recovery_enabled = false
    }
    
    
    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }

  deletion_protection = false
}

resource "google_sql_database" "product_db" {
  provider = google
  name     = "products"
  instance = google_sql_database_instance.primary.name
}

resource "google_sql_user" "default_user" {
  provider = google
  name     = "postgres"
  instance = google_sql_database_instance.primary.name
  password = "Kirti#13" 
}

output "db_instance_connection_name" {
  value       = google_sql_database_instance.primary.connection_name
  description = "The connection name for the Cloud SQL instance."
}

output "db_public_ip" {
  value       = google_sql_database_instance.primary.public_ip_address
  description = "The public IP address of the Cloud SQL instance."
}