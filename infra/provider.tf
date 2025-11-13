
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "oceanic-spot-477008-k6"
  region  = "asia-south1"
}