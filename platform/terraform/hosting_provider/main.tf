terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.50"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.5.1"
    }
  }
}

provider "azurerm" {
  features {}
}

module "hosting-provider-azure" {
  source = "../modules/cloud_azure"

  resource_group_name = "DevX-rg"
  location            = "westeurope"
  aks_cluster_name    = "DevXAks"

  # Default node group
  default_node_pool_vm_size            = "Standard_B2s"
  default_node_pool_availability_zones = ["2", "3"]
  default_node_pool_min_count          = 1
  default_node_pool_max_count          = 5
  default_node_pool_node_count         = 3

  tags = {
    createdWith   = "Terraform"
    ProvisionedBy = "local"
  }
}