# All generic output goes here

# Each provider's output.tf needs to define a controller_ip_map. This
# map is used to build the Ansible controller's ssh configuration.
# Each map entry contains the node's hostname and public/private IP
# address.
output "controller_ip_map" {
  description = "The IP addresses assigned to each instance"
  value = zipmap(var.kdevops_nodes[*],
  google_compute_instance.kdevops_instance[*].network_interface[0].access_config[0].nat_ip)
}

output "cloud_build_bucket" {
  description = "GCS bucket for Cloud Build kernel artifacts"
  value       = var.gce_cloud_build_enabled ? module.kdevops_cloud_build[0].bucket_name : ""
}

output "cloud_build_bucket_url" {
  description = "URL of the GCS bucket for kernel artifacts"
  value       = var.gce_cloud_build_enabled ? module.kdevops_cloud_build[0].bucket_url : ""
}

output "cloud_build_service_account" {
  description = "Email of the Cloud Build service account"
  value       = var.gce_cloud_build_enabled ? module.kdevops_cloud_build[0].service_account_email : ""
}
