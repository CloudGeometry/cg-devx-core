# Google Cloud Client Config and Kubernetes Provider Configuration
data "google_client_config" "default" {}

provider "kubernetes" {
  host                   = "https://${module.gke.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke.ca_certificate)
}

# GKE Cluster Configuration
module "gke" {
  source = "terraform-google-modules/kubernetes-engine/google//modules/private-cluster"

  name            = local.name
  project_id      = local.project_id
  region          = local.region
  release_channel = "STABLE"

  enable_private_endpoint = false
  enable_private_nodes    = true
  create_service_account  = true
  deletion_protection     = false
  master_ipv4_cidr_block  = cidrsubnet(local.vpc_cidr, 12, 1024)

  network           = module.vpc.network_name
  subnetwork        = lookup(module.vpc.subnets, "${local.region}/${local.name}-private").name
  ip_range_pods     = "${local.name}-gke-pods"
  ip_range_services = "${local.name}-gke-services"

  dns_cache                  = true
  enable_shielded_nodes      = true
  filestore_csi_driver       = false
  gce_pd_csi_driver          = true
  horizontal_pod_autoscaling = local.enable_native_auto_scaling
  http_load_balancing        = false
  network_policy             = false
  remove_default_node_pool   = true

  node_pools = [
    for np in local.gke_node_groups : {
      name               = np.name
      machine_type       = np.instance_types[0]
      min_count          = np.min_size
      max_count          = np.max_size
      initial_node_count = np.desired_size
      local_ssd_count    = 0
      spot               = np.capacity_type == "SPOT"
      disk_size_gb       = np.disk_size
      disk_type          = "pd-standard"
      image_type         = "COS_CONTAINERD"
      enable_gcfs        = false
      enable_gvnic       = false
      auto_repair        = true
      auto_upgrade       = true
      preemptible        = np.capacity_type == "SPOT"
    }
  ]
}
