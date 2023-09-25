/**
 * Global variables
 */
variable "region" {
  description = "Specifies the location for the resource group and all the resources"
  default     = "westeurope"
  type        = string
}

variable "tags" {
  description = "(Optional) Specifies tags for all the resources"
  default = {
    createdWith = "Terraform"
  }
}

variable "resource_group_name" {
  description = "Specifies the resource group name"
  default     = "DevX-rg"
  type        = string
}

/**
 * Log analytics variables
 */

variable "log_analytics_workspace_name" {
  description = "Specifies the name of the log analytics workspace"
  default     = "DevXAksWorkspace"
  type        = string
}

variable "log_analytics_retention_days" {
  description = "Specifies the number of days of the retention policy"
  type        = number
  default     = 15
}

/**
 * Netowrking configuration
 */

variable "cluster_network_cidr" {
  type = string
  default = "10.0.0.0/16"
}

variable "vnet_name" {
  type = string
  default = "DevXAksVNet"
}

variable "subnets" {
  type = list(string)
  description = "maximum 16"
  default = [
    "pub", "priv", "int"
  ]  
}

# variable "networks" {
#   default = {
#     hub = {
#       vnet_name     = "DevXHubVNet",
#       address_space = ["10.1.0.0/16"]
#       subnets = [
#         {
#           name = "AzureFirewallSubnet"
#           #address_prefixes                              = ["10.1.0.0/24"]
#           private_endpoint_network_policies_enabled     = true
#           private_link_service_network_policies_enabled = false
#         }
#       ]
#     },
#     aks = {
#       vnet_name     = "DevXAksVNet",
#       address_space = ["10.0.0.0/16"],
#       subnets = [
#         {
#           name = "SystemSubnet"
#           #address_prefixes                              = ["10.0.0.0/20"]
#           private_endpoint_network_policies_enabled     = true
#           private_link_service_network_policies_enabled = false
#         },
#         {
#           name = "UserSubnet"
#           #address_prefixes                              = ["10.0.16.0/20"]
#           private_endpoint_network_policies_enabled     = true
#           private_link_service_network_policies_enabled = false
#         },
#         {
#           name = "PodSubnet"
#           #address_prefixes                              = ["10.0.32.0/20"]
#           private_endpoint_network_policies_enabled     = true
#           private_link_service_network_policies_enabled = false
#         },
#         {
#           name = "DevXGeneralSubnet"
#           #address_prefixes                              = ["10.0.48.0/20"]
#           private_endpoint_network_policies_enabled     = true
#           private_link_service_network_policies_enabled = false
#         }
#       ]
#     }
#   }
#   type = map(any)
# }

/**
 * Firewall variables
 */

variable "firewall_name" {
  description = "Specifies the name of the Azure Firewall"
  default     = "DevXFirewall"
  type        = string
}

/**
 * routing variables
 */

variable "route_table_name" {
  type    = string
  default = "DefaultRouteTable"
}

variable "route_name" {
  type    = string
  default = "RouteToAzureFirewall"
}

/**
 * AKS cluster variables
 */

variable "cluster_name" {
  description = "(Required) Specifies the name of the AKS cluster."
  default     = "DevXAks"
  type        = string
}

variable "aks_private_cluster" {
  type    = bool
  default = false
}

variable "admin_group_object_ids" {
  description = "(Optional) A list of Object IDs of Azure Active Directory Groups which should have Admin Role on the Cluster."
  default     = ["6e5de8c1-5a4b-409b-994f-0706e4403b77", "78761057-c58c-44b7-aaa7-ce1639c6c4f5"]
  type        = list(string)
}

variable "default_node_pool_vm_size" {
  description = "Specifies the vm size of the default node pool"
  default     = "Standard_B2s"
  type        = string
}

variable "default_node_pool_availability_zones" {
  description = "Specifies the availability zones of the default node pool"
  default     = ["2", "3"]
  type        = list(string)
}

variable "network_dns_service_ip" {
  description = "Specifies the DNS service IP"
  default     = "10.2.0.10"
  type        = string
}

variable "network_service_cidr" {
  description = "Specifies the service CIDR"
  default     = "10.2.0.0/24"
  type        = string
}

variable "default_node_pool_max_count" {
  description = "(Required) The maximum number of nodes which should exist within this Node Pool. Valid values are between 0 and 1000 and must be greater than or equal to min_count."
  type        = number
  default     = 5
}

variable "default_node_pool_min_count" {
  description = "(Required) The minimum number of nodes which should exist within this Node Pool. Valid values are between 0 and 1000 and must be less than or equal to max_count."
  type        = number
  default     = 1
}

variable "default_node_pool_node_count" {
  description = "(Optional) The initial number of nodes which should exist within this Node Pool. Valid values are between 0 and 1000 and must be a value in the range min_count - max_count."
  type        = number
  default     = 3
}
variable "ssh_public_key" {
  description = "(Required) Specifies the SSH public key for AKS worker nodes."
  type        = string
  default     = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCzkaoqP5dPnw+9p2mwo2ZVkft970st3sd0PmTV/Q4kKVCmPE3PilwSMN3ryWGuSUqkWUXkOypFMw83DU06HwvOv2o+KJxMUZRSswaHbpU4HmjGlK8zkQAz0IRGOCcW+CiLnNbVgjq7jB6ESD9yRU4XhmEb1TGt7wmQgKkWqR1hmsd0jDCzQHHztuWbeipjeNsJhpSMzJD9iv7/tdPrnBABZ4/4mS9h8NfOVokbXVcgG30qZM6RHH0PUiWaem5ntA2WXHjjTa2oGDPy3p4jC+O8C2yXY7VgqN5cGSmmIpBGc9qrZhDNx+1ZtGOUp8fEotZ5KHtzPmPqdvz86Fq45y2j mikhailkhviadchenia@Mikhails-MBP"
}

variable "workload_identity_enabled" {
  description = "(Optional) Specifies whether Azure AD Workload Identity should be enabled for the Cluster. Defaults to false."
  type        = bool
  default     = true
}

/**
 * Storage account variables
 */
/* variable "storage_account_prefix" {
  type    = string
  default = "boot"
} */

/**
 * Key vault variables
 */

variable "key_vault_enabled_for_deployment" {
  description = "(Optional) Boolean flag to specify whether Azure Virtual Machines are permitted to retrieve certificates stored as secrets from the key vault. Defaults to false."
  type        = bool
  default     = true
}

variable "key_vault_enabled_for_disk_encryption" {
  description = " (Optional) Boolean flag to specify whether Azure Disk Encryption is permitted to retrieve secrets from the vault and unwrap keys. Defaults to false."
  type        = bool
  default     = true
}

variable "key_vault_enabled_for_template_deployment" {
  description = "(Optional) Boolean flag to specify whether Azure Resource Manager is permitted to retrieve secrets from the key vault. Defaults to false."
  type        = bool
  default     = true
}

variable "key_vault_enable_rbac_authorization" {
  description = "(Optional) Boolean flag to specify whether Azure Key Vault uses Role Based Access Control (RBAC) for authorization of data actions. Defaults to false."
  type        = bool
  default     = true
}

variable "key_vault_purge_protection_enabled" {
  description = "(Optional) Is Purge Protection enabled for this Key Vault? Defaults to false."
  type        = bool
  default     = true
}

/**
 * Private DNS zone variables
 */

variable "private_dns_zones" {
  type = map(any)
  default = {
    "KeyVaultPrivate" = "privatelink.vaultcore.azure.net",
    "BlobPrivate"     = "privatelink.blob.core.windows.net"
  }
}


/**
 * extra node pools variables
 */

variable "additional_node_pools" {
  type    = any
  default = []
  validation {
    condition     = alltrue([for i in var.additional_node_pools : can(i.node_pool_name)])
    error_message = "All extra node pools have to have `node_pool_name` field specified."
  }
}

/**
 * defaults for all extra node pools
 * if not specified in list those variables will be used
 */

variable "additional_node_pool_name" {
  description = "(Required) Specifies the name of the node pool."
  type        = string
  default     = "user"
}

variable "additional_node_pool_vm_size" {
  description = "(Required) The SKU which should be used for the Virtual Machines used in this Node Pool. Changing this forces a new resource to be created."
  type        = string
  default     = "Standard_B2s_v2"
}

variable "additional_node_pool_max_count" {
  description = "(Required) The maximum number of nodes which should exist within this Node Pool. Valid values are between 0 and 1000 and must be greater than or equal to min_count."
  type        = number
  default     = 5
}

variable "additional_node_pool_min_count" {
  description = "(Required) The minimum number of nodes which should exist within this Node Pool. Valid values are between 0 and 1000 and must be less than or equal to max_count."
  type        = number
  default     = 3
}

variable "additional_node_pool_node_count" {
  type    = number
  default = 3
}

variable "additional_node_pool_availability_zones" {
  type    = list(string)
  default = ["2", "3"]
}

variable "additional_node_pool_enable_auto_scaling" {
  type    = bool
  default = true
}

variable "cluster_version" {
  description = "(Optional )Specifies the AKS Kubernetes version"
  default     = "1.26"
  type        = string
}
variable "service_accounts" {
  description = "Specifies the AKS SA names and roles."
  type        = map(any)
  default = {
    sa_1 = {
      name = "atlantis"
      role_definition_name = "Contributor"
    }
    sa_2 = {
      name = "dns"
      role_definition_name = "DNS Zone Contributor"
    }
  }
}