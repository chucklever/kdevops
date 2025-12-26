variable "cb_project" {
  description = "GCE project ID for Cloud Build resources"
  type        = string
}

variable "cb_region" {
  description = "GCE region for the artifact bucket"
  type        = string
}

variable "cb_bucket_name" {
  description = "Name for the GCS artifact bucket (auto-generated if empty)"
  type        = string
  default     = ""
}

variable "cb_artifact_retention_days" {
  description = "Number of days to retain kernel artifacts before deletion"
  type        = number
  default     = 30
}

variable "cb_force_destroy" {
  description = "Allow bucket deletion even when non-empty. Set to true only for development or testing environments; production should keep this false to prevent accidental data loss."
  type        = bool
  default     = false
}

variable "cb_service_account_id" {
  description = "Service account ID for Cloud Build operations"
  type        = string
  default     = "kdevops-cloud-build"
}
