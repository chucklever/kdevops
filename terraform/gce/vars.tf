variable "gce_credentials" {
  description = "Path to the your service account JSON credentials file"
  type        = string
}

variable "gce_disk_count" {
  description = "Count of attached disks per instance"
  type        = number
}

variable "gce_disk_iops" {
  description = "Provisioned IOPS for each attached disk"
  type        = number
  default     = null
}

variable "gce_disk_size" {
  description = "Size of each attached disk, in GB"
  type        = number
}

variable "gce_disk_throughput" {
  description = "Provisioned throughput for each attached disk"
  type        = number
  default     = null
}

variable "gce_disk_type" {
  description = "Performance class of attached disks"
  type        = string
}

variable "gce_image_family" {
  description = "Release of Linux distribution"
  type        = string
}

variable "gce_image_project" {
  description = "Name of Linux distribution"
  type        = string
}

variable "gce_image_size" {
  description = "Size of image, in GiB"
  type        = number
}

variable "gce_image_type" {
  description = "Type of image disk"
  type        = string
}

variable "gce_machine_type" {
  description = "Machine type"
  type        = string
}

variable "gce_project" {
  description = "Your project name"
  type        = string
}

variable "gce_region" {
  description = "Geographic Region"
  type        = string
}

variable "gce_zone" {
  description = "Availability zone"
  type        = string
}

variable "gce_cloud_build_enabled" {
  description = "Enable Cloud Build infrastructure"
  type        = bool
  default     = false
}

variable "gce_cloud_build_bucket" {
  description = "GCS bucket name for kernel artifacts (auto-generated if empty)"
  type        = string
  default     = ""
}

variable "gce_cloud_build_retention_days" {
  description = "Number of days to retain kernel artifacts"
  type        = number
  default     = 30
}

variable "gce_cloud_build_service_account_id" {
  description = "Service account ID for Cloud Build operations"
  type        = string
}
