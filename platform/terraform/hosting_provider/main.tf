provider "azurerm" {
  features {}
}


module "hosting-provider-azure" {
  source = "../modules/cloud_azure"

  region          = "westeurope"
  cluster_name    = "devxaks" # only letters and numbers
  cluster_version = "1.26"

  # Default node group
  default_node_pool_vm_size            = "Standard_B2s"
  default_node_pool_availability_zones = ["1"]
  default_node_pool_min_count          = 1
  default_node_pool_max_count          = 5
  default_node_pool_node_count         = 3

  # Additional node groups
  # omited variables will be substitued by module-wide 
  # additional_node_pool_* variables
  additional_node_pools = [
    {
      node_pool_name               = "additional1"
      node_pool_vm_size            = "Standard_B2s"
      node_pool_min_count          = 1
      node_pool_max_count          = 3
      node_pool_node_count         = 1
      node_pool_availability_zones = ["2", "3"]
    },
    {
      node_pool_name               = "additional2"
      node_pool_availability_zones = ["2"]
    }
  ]
  additional_node_pool_min_count = 2

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


/* output "private_ip_address" {
  description = "Specifies the private IP address of the firewall."
  value       = module.hosting-provider-azure.public_ip_address
} */


output "fqdn" {
  value       = module.hosting-provider-azure.fqdn
  description = "he FQDN of the Azure Kubernetes Managed Cluster."
}