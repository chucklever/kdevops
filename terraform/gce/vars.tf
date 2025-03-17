variable "gce_credentials_file" {
  description = "Path to the your service account JSON credentials file"
  type        = string
  default     = "invalid"
}

variable "gce_image_type" {
  description = "Type of image disk"
  type        = string
  default     = "invalid"
}

variable "gce_machine_type" {
  description = "Machine type"
  type        = string
  default     = "invalid"
}

variable "gce_project" {
  description = "Your project name"
  type        = string
  default     = "invalid"
}

variable "gce_region" {
  description = "Geographic Region"
  type        = string
  default     = "invalid"
}

variable "gce_zone" {
  description = "Availability zone"
  type        = string
  default     = "invalid"
}

variable "image_name" {
  description = "Name of image to use"
  default     = "debian-cloud/debian-10"
}

variable "scratch_disk_interface" {
  description = "The type of interface for the scratch disk, SCSI, or NVME"
  default     = "NVME"
}
