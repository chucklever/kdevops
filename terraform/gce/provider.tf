terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~>6.25"
    }
    null = {
      source  = "hashicorp/null"
      version = "~>2.1"
    }
  }
}

provider "google" {
  credentials = file(var.gce_credentials_file)
  project     = var.gce_project
  region      = var.gce_region
}
