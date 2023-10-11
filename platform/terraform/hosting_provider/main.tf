provider "azurerm" {
  features {}
  /* azure SP info Sponsorship subscription*/
  subscription_id = "589bdbcd-8edc-42f6-9898-e0eb44a19e04"
  tenant_id       = "fbd4a7eb-f866-4926-9aff-4a972cdef121"
  client_id       = "1f7fba2a-351e-4a1b-8ae1-bef42cec610e"
  client_secret   = "btnI3EhQZMYVo.4~96Zuy4BCg5djUyvCo4"
  /* Azure SP info Visual Studio Enterprise Subscription - MCT /
 /*  subscription_id   = "357a6301-ef79-489e-ba9e-10ce2267585b"
  tenant_id         = "fbd4a7eb-f866-4926-9aff-4a972cdef121"
  client_id         = "2cf60ee4-db67-43e1-ab59-e6764fb5c429"
  client_secret     = "LZnPxAPUrR50rGH9xF_WPWUmvN77h6d_vT" */
}


module "hosting-provider-azure" {
  source = "../modules/cloud_azure"

  region               = "westeurope"
  cluster_name         = "devxaks" # only letters and numbers
  cluster_version      = "1.26"
  cluster_network_cidr = "10.1.0.0/16"

  # # Default node group
  # default_node_pool_vm_size            = "Standard_B2s"
  # default_node_pool_availability_zones = ["1"]
  # default_node_pool_min_count          = 1
  # default_node_pool_max_count          = 5
  # default_node_pool_node_count         = 3

  # # Additional node groups
  # # omited variables will be substitued by module-wide 
  # # additional_node_pool_* variables
  # additional_node_pools = [
  #   {
  #     node_pool_name               = "additional1"
  #     node_pool_vm_size            = "Standard_B2s"
  #     node_pool_min_count          = 1
  #     node_pool_max_count          = 3
  #     node_pool_node_count         = 1
  #     node_pool_availability_zones = ["2", "3"]
  #   },
  #   {
  #     node_pool_name               = "additional2"
  #     node_pool_availability_zones = ["2"]
  #   }
  # ]
  # additional_node_pool_min_count = 2

  az_count = 2
  node_groups = [
    {
      name          = "default",
      instance_type = "Standard_B2s",
      min_size      = 1,
      max_size      = 5,
      desired_size  = 3
      }, {
      name          = "extra",
      instance_type = "Standard_B2s_v2",
      min_size      = 1,
      max_size      = 1,
      desired_size  = 1
    }
  ]
  cluster_node_labels = {
    "Provisioned-By" = "Terraform"
  }
  tags = {
    createdWith   = "Terraform"
    ProvisionedBy = "local"
  }
}

# Output part 
output "kube_config_raw" {
  value       = module.hosting-provider-azure.kube_config_raw
  sensitive   = true
  description = "Contains the Kubernetes config to be used by kubectl and other compatible tools."
}


output "fqdn" {
  value       = module.hosting-provider-azure.fqdn
  description = "FQDN of the Azure Kubernetes Managed Cluster"
}

output "apps" {
  value       = module.hosting-provider-azure.apps
  description = "Name and ID for all AKS Rbac apps"
}
