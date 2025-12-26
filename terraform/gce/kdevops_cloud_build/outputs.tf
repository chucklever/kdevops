output "bucket_name" {
  description = "Name of the GCS bucket for kernel artifacts"
  value       = google_storage_bucket.kernel_artifacts.name
}

output "bucket_url" {
  description = "URL of the GCS bucket for kernel artifacts"
  value       = google_storage_bucket.kernel_artifacts.url
}

output "service_account_email" {
  description = "Email of the Cloud Build service account"
  value       = google_service_account.cloud_build.email
}
