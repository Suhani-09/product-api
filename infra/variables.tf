variable "db_password" {
  description = "The password for the Cloud SQL postgres user"
  type        = string
  sensitive   = true
}
