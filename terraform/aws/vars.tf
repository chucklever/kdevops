variable "aws_region" {
  description = "Your preferred AWS region"
  type        = string
}

variable "aws_availability_zone" {
  description = "Your preferred AWS availability zone"
  type        = string
}

variable "ssh_keyname" {
  description = "The name of your ssh key, this is just the name displayed and used on aws in the backend"
  default     = "kdevops_aws_key"
}

variable "ssh_pubkey_data" {
  description = "The ssh public key data"

  # for instance it coudl be "ssh-rsa AAetcccc"
  default = ""
}

variable "aws_name_search" {
  description = "Your AWS AMI name search filter expression"
  type        = string
}

variable "aws_ami_owner" {
  description = "An AWS AMI image owner or owner alias"
  type        = string
}

variable "aws_instance_type" {
  description = "Your AWS instance type"
  type        = string
}

variable "aws_enable_ebs" {
  description = "Whether or not to enable EBS"
  default     = "no"
}

variable "aws_ebs_volumes_per_instance" {
  description = "Number of EBS volumes to create per instance"
  type        = number
}

# The t2.micro comes with 8 GiB of storage.
# For more storage we need to use EBS.
# AWS Free Tier includes 30GB of Storage, 2 million I/Os, and 1GB of snapshot
# storage with Amazon Elastic Block Store (EBS).
#
variable "aws_ebs_volume_size" {
  description = "Size in GiB for each of the volumes"
  default     = "4"
}

variable "aws_ebs_volume_type" {
  description = "Type of each of the EBS volumes"
  default     = "gp2"
}

variable "aws_ebs_volume_iops" {
  description = "IOPS reserved for each EBS volume"
  type        = number
  default     = null
}

# We had to use this as aws terraform provider doesn't have a way to set
# the hostname. local-exec works too, but this is what we went with.
variable "user_data_enabled" {
  description = "Do you want to enable cloud-init user data processing?"
  default     = "yes"
}

variable "user_data_log_dir" {
  description = "Where on the node you want user_data processing logs to go"
  default     = "/var/log/user_data"
}

# Disable for non-systemd systems, you'll want to implement something that
# does all what systemd does for us then if you still want your hostname
# changed.
variable "user_data_admin_enable_hostnamectl" {
  description = "Should we use hostnamectl to change the target hostname?"
  default     = "yes"
}

# kdevops does want us to have the hostname there, yes... so this is required.
# I forget which tests requires this.
variable "user_data_admin_enable_host_file" {
  description = "Should /etc/hosts also be appended with the new hostname with the localhost address?"
  default     = "yes"
}

# So far there hasn't been a need to configure this value
variable "aws_shared_config_file" {
  description = "Shared AWS configuration file"
  type        = string
  default     = "~/.aws/conf"
}

# So far there hasn't been a need to configure this value
variable "aws_shared_credentials_file" {
  description = "Shared AWS credentials file"
  type        = string
  default     = "~/.aws/credentials"
}

variable "aws_profile" {
  description = "AWS user profile"
  type        = string
}
