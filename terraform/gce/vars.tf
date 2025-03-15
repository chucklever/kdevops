variable "gce_credentials_file" {
  description = "Path to the your service account JSON credentials file"
  type        = string
  default     = "invalid"
}

variable "gce_project" {
  description = "Your project name"
  type        = string
  default     = "invalid"
}

# https://cloud.google.com/compute/docs/regions-zones/
# This is LA, California
variable "region" {
  description = "Region location"
  default     = "us-west2-c"
}

# https://cloud.google.com/compute/docs/machine-types
variable "machine_type" {
  description = "Machine type"
  default     = "n1-standard-1"
}

variable "image_name" {
  description = "Name of image to use"
  default     = "debian-cloud/debian-10"
}

variable "scratch_disk_interface" {
  description = "The type of interface for the scratch disk, SCSI, or NVME"
  default     = "NVME"
}
