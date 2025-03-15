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

variable "gce_image_project" {
  description = "Name of Linux distribution"
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

variable "gce_image_family" {
  description = "Release of Linux distribution"
  default     = "invalid"
}

variable "gce_image_size" {
  description = "Size of image, in GiB"
  type        = number
  default     = 0
}

variable "scratch_disk_interface" {
  description = "The type of interface for the scratch disk, SCSI, or NVME"
  default     = "NVME"
}
