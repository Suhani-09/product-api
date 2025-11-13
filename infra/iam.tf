
resource "google_service_account" "product_api_gsa" {
  account_id   = "product-api-gsa"
  display_name = "Product API Service Account"
  description  = "Service account for Product API to access Cloud SQL"
}


resource "google_project_iam_member" "product_api_sql_client" {
  project = "oceanic-spot-477008-k6"
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.product_api_gsa.email}"
}


resource "google_service_account_iam_member" "workload_identity_binding" {
  service_account_id = google_service_account.product_api_gsa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:oceanic-spot-477008-k6.svc.id.goog[default/product-api-ksa]"
}


output "gsa_email" {
  value       = google_service_account.product_api_gsa.email
  description = "Email of the Google Service Account"
}