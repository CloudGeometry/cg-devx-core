terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.16.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5.1"
    }
  }
  backend "gcs" {
    bucket = "cgdevx-test-bucket"
    prefix = "terraform/google/terraform.tfstate"
  }
}

provider "google" {
  project = local.project_id
  region  = local.region
}

locals {
  name                    = var.cluster_name
  cluster_version         = var.cluster_version
  region                  = var.region
  project_id              = "cg-devx-test"
  vpc_cidr                = var.cluster_network_cidr
  azs                     = [for i in range(1, var.az_count + 1) : tostring(i)]
  cluster_node_labels     = var.cluster_node_labels
  //node_group_type         = var.node_group_type
  tags                    = var.tags
  node_labels_substr      = join(",", formatlist("%s=%s", keys(var.cluster_node_labels), values(var.cluster_node_labels)))
  default_node_group_name = "${local.name}-node-group"
  eks_node_groups         = [
    for node_group in var.node_groups :
    {
      name           = node_group.name == "" ? local.default_node_group_name : node_group.name
      min_size       = node_group.min_size
      max_size       = node_group.max_size
      desired_size   = node_group.desired_size
      instance_types = node_group.instance_types
      capacity_type  = upper(node_group.capacity_type)
      labels         = merge(
        { "node.kubernetes.io/lifecycle" = node_group.capacity_type },
        var.cluster_node_labels
      )
    }
  ]
  //log_analytics_retention_days = 30


  //default_node_group         = var.node_groups[0]
  //additional_node_pools      = try(slice(var.node_groups, 1, length(var.node_groups)), [])
  //max_pods                   = 100
  //node_admin_username        = "gcpadmin"
  enable_native_auto_scaling = var.enable_native_auto_scaling
}

#resource "azurerm_resource_group" "rg" {
#  name     = "${local.name}-rg"
#location = var.region
#tags     = local.tags
#}


