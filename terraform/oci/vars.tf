variable "oci_region" {
  description = "An OCI region"
  default = ""
}

variable "oci_tenancy_ocid" {
  description = "OCID of your tenancy"
  default = ""
}

variable "oci_user_ocid" {
  description = "OCID of the user calling the API"
  default = ""
}

variable "oci_user_private_key_path" {
  description = "The path of the private key stored on your computer"
  default = ""
}

variable "oci_user_fingerprint" {
  description = "Fingerprint for the key pair being used"
  default = ""
}

variable "oci_availablity_domain" {
  description = "Name of availability domain"
  default = ""
}

variable "oci_compartment_ocid" {
  description = "OCID of compartment"
  default = ""
}

variable "oci_shape" {
  description = "Shape name"
  default = ""
}

variable "oci_instance_flex_ocpus" {
  description = "The total number of OCPUs available to the instance."
  type = number
  default = null
}

variable "oci_instance_flex_memory_in_gbs" {
  description = "The total amount of memory available to the instance, in gigabytes."
  type = number
  default = null
}

variable "oci_os_image_ocid" {
  description = "OCID of OS image"
  default = ""
}

variable "oci_assign_public_ip" {
  description = "Assign public IP to the instance"
  default = false
}

variable "oci_subnet_ocid" {
  description = "Subnet OCID"
  default = ""
}

variable "oci_volumes_enable_extra" {
  description = "Create additional block volumes per instance"
  default     = false
}

variable "oci_volumes_per_instance" {
  description = "The count of additional block volumes per instance"
  type        = number
  default     = 0
}

variable "oci_volumes_size" {
  description = "The size of additional block volumes, in gibibytes"
  type        = number
  default     = 0
}

variable "oci_data_volume_display_name" {
  description = "Display name to use for the data volume"
  default = "data"
}

variable oci_data_volume_device_file_name {
  description = "Data volume's device file name"
  default = "/dev/oracleoci/oraclevdb"
}

variable "oci_sparse_volume_display_name" {
  description = "Display name to use for the sparse volume"
  default = "sparse"
}

variable oci_sparse_volume_device_file_name {
  description = "Sparse volume's device file name"
  default = "/dev/oracleoci/oraclevdc"
}
