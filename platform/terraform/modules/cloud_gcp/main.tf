terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.40.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5.1"
    }
  }
}
data "google_project" "project" {}
locals {
  name                    = var.cluster_name
  cluster_version         = var.cluster_version
  region                  = var.region
  project_id              = data.google_project.project.project_id
  vpc_cidr                = var.cluster_network_cidr
  azs                     = [for i in range(1, var.az_count + 1) : tostring(i)]
  cluster_node_labels     = var.cluster_node_labels
  tags                    = var.tags
  node_labels_substr      = join(",", formatlist("%s=%s", keys(var.cluster_node_labels), values(var.cluster_node_labels)))
  default_node_group_name = "${local.name}-node-group"
  ci_sa_workloads         = [
    for key, _ in var.workloads : {
      namespace = "wl-${key}-build"
      name      = "argo-workflow"
    }
  ]
  gke_node_groups = [
    for node_group in var.node_groups :
    {
      name           = node_group.name == "" ? local.default_node_group_name : node_group.name
      min_size       = node_group.min_size
      max_size       = node_group.max_size
      desired_size   = node_group.desired_size
      disk_size      = node_group.disk_size
      instance_types = node_group.instance_types
      capacity_type  = upper(node_group.capacity_type)
      labels         = merge(
        { "node.kubernetes.io/lifecycle" = node_group.capacity_type },
        var.cluster_node_labels
      )
    }
  ]
  enable_native_auto_scaling = var.enable_native_auto_scaling
}
