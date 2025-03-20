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

variable "azure_image_offer" {
  description = "OS image offer"
  type        = string
  default     = "invalid"
}

variable "azure_image_publisher" {
  description = "OS image publisher"
  type        = string
  default     = "invalid"
}

variable "azure_image_sku" {
  description = "OS image SKU"
  type        = string
  default     = "invalid"
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

variable "azure_vmsize" {
  description = "VM size"
  type        = string
  default     = "invalid"
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
