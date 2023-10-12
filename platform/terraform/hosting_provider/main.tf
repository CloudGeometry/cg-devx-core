provider "azurerm" {
  features {}
}


module "hosting-provider-azure" {
  source = "../modules/cloud_azure"

  region               = "westeurope"
  cluster_name         = "devxaks" # only letters and numbers
  cluster_version      = "1.26"
  cluster_network_cidr = "10.1.0.0/16"

  az_count = 1
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
