# Cloud Build infrastructure for kdevops kernel builds
#
# This module provisions the GCS bucket and service account required
# for Cloud Build to compile and store kernel packages.

# Generate a unique suffix for globally unique bucket names
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

locals {
  # Use provided bucket name or generate one from project
  bucket_name = var.cb_bucket_name != "" ? var.cb_bucket_name : format(
    "%s-kdevops-kernels-%s",
    var.cb_project,
    random_id.bucket_suffix.hex
  )
}

# GCS bucket for kernel build artifacts
resource "google_storage_bucket" "kernel_artifacts" {
  name          = local.bucket_name
  location      = var.cb_region
  project       = var.cb_project
  force_destroy = var.cb_force_destroy

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = var.cb_artifact_retention_days
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    purpose = "kdevops-kernel-builds"
  }
}

# Service account for Cloud Build operations
resource "google_service_account" "cloud_build" {
  account_id   = var.cb_service_account_id
  display_name = format("%s Service Account", var.cb_service_account_id)
  project      = var.cb_project
}

# Grant Cloud Build service account access to the artifact bucket
resource "google_storage_bucket_iam_member" "cloud_build_bucket_access" {
  bucket = google_storage_bucket.kernel_artifacts.name
  role   = "roles/storage.objectAdmin"
  member = format("serviceAccount:%s", google_service_account.cloud_build.email)
}

# Grant Cloud Build permissions to the service account
resource "google_project_iam_member" "cloud_build_builder" {
  project = var.cb_project
  role    = "roles/cloudbuild.builds.builder"
  member  = format("serviceAccount:%s", google_service_account.cloud_build.email)
}

# Grant logging permissions for build logs
resource "google_project_iam_member" "cloud_build_logs" {
  project = var.cb_project
  role    = "roles/logging.logWriter"
  member  = format("serviceAccount:%s", google_service_account.cloud_build.email)
}
