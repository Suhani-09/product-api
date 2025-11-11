# Set up the Terraform provider for Google Cloud
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Configure the Google Cloud provider
provider "google" {
  project = "oceanic-spot-477008-k6"
  region  = "asia-south1"
}