variable "azure_application_id" {
  description = "Your application ID"
  type        = string
  default     = null
}

variable "azure_client_certificate_password" {
  description = "The password to the service principal PFX certificate file"
  type        = string
  default     = null
}

variable "azure_client_certificate_path" {
  description = "Path to the service principal PFX certificate file"
  type        = string
  default     = null
}

variable "azure_location" {
  description = "Azure resource location"
  type        = string
  default     = "invalid"
}

variable "azure_subscription_id" {
  description = "Your Azure subscription ID"
  type        = string
  default     = "invalid"
}

variable "azure_tenant_id" {
  description = "Your Azure tenant ID"
  type        = string
  default     = null
}

variable "vmsize" {
  description = "VM size"
  default     = "Standard_DS3_v2"
}

variable "image_publisher" {
  description = "Storage image publisher"
  default     = "Debian"
}

variable "image_offer" {
  description = "Storage image offer"
  default     = "debian-10"
}

variable "image_sku" {
  description = "Storage image sku"
  default     = "10"
}

variable "image_version" {
  description = "Storage image version"
  default     = "latest"
}

variable "managed_disks_per_instance" {
  description = "Count of managed disks per VM instance"
  type        = number
  default     = 0
}

variable "managed_disks_size" {
  description = "Size of each managed disk, in gibibytes"
  type        = number
  default     = 0
}
