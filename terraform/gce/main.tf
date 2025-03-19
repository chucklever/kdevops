data "google_compute_image" "kdevops_image" {
  project = var.gce_image_project
  family  = var.gce_image_family
}

resource "google_compute_network" "kdevops_network" {
  auto_create_subnetworks      = false
  bgp_best_path_selection_mode = "STANDARD"
  mtu                          = 1500
  name                         = "kdevops-vpc"
  routing_mode                 = "REGIONAL"
}

resource "google_compute_subnetwork" "kdevops_subnetwork" {
  ip_cidr_range = "10.0.0.0/24"
  name          = "kdevops-subnet"
  network       = google_compute_network.kdevops_network.id
  region        = var.gce_region
}

resource "google_compute_network_attachment" "kdevops_network_attachment" {
  connection_preference = "ACCEPT_AUTOMATIC"
  name                  = "kdevops-net-attachment"
  region                = var.gce_region
  subnetworks           = [google_compute_subnetwork.kdevops_subnetwork.id]
}

resource "google_compute_instance" "kdevops_instance" {
  count        = local.kdevops_num_boxes
  name         = element(var.kdevops_nodes, count.index)
  machine_type = var.gce_machine_type
  zone         = var.gce_zone

  tags = ["kdevops"]

  boot_disk {
    initialize_params {
      image = data.google_compute_image.kdevops_image.self_link
      size  = var.gce_image_size
      type  = var.gce_image_type
    }
  }

  network_interface {
    network = "default"

    # Ephemeral IP
    access_config {
    }
  }

  network_interface {
    network_attachment = google_compute_network_attachment.kdevops_network_attachment.self_link
  }

  lifecycle {
    ignore_changes = [attached_disk]
  }

  metadata = {
    ssh-keys = format("%s:%s", var.ssh_config_user, file(var.ssh_config_pubkey_file))
  }

  metadata_startup_script = "echo hi > /test.txt"
}

module "kdevops_compute_disks" {
  count              = local.kdevops_num_boxes
  cd_disk_count      = var.gce_disk_count
  cd_disk_iops       = var.gce_disk_iops
  cd_disk_size       = var.gce_disk_size
  cd_disk_throughput = var.gce_disk_throughput
  cd_disk_type       = var.gce_disk_type
  cd_instance_id     = google_compute_instance.kdevops_instance[count.index].id
  cd_instance_name   = element(var.kdevops_nodes, count.index)
  cd_zone            = var.gce_zone
  source             = "./kdevops_compute_disks"
}
