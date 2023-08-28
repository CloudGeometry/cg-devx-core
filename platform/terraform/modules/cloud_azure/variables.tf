/**
 * Global variables
 */
variable "location" {
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
  default     = 30
}

/**
 * Netowrking configuration
 */


variable "networks" {
  default = {
    hub = {
      vnet_name     = "DevXHubVNet",
      address_space = ["10.1.0.0/16"]
      subnets = [
        {
          name                                          = "AzureFirewallSubnet"
          address_prefixes                              = ["10.1.0.0/24"]
          private_endpoint_network_policies_enabled     = true
          private_link_service_network_policies_enabled = false
        }
      ]
    },
    aks = {
      vnet_name     = "DevXAksVNet",
      address_space = ["10.0.0.0/16"],
      subnets = [
        {
          name                                          = "SystemSubnet"
          address_prefixes                              = ["10.0.0.0/20"]
          private_endpoint_network_policies_enabled     = true
          private_link_service_network_policies_enabled = false
        },
        {
          name                                          = "UserSubnet"
          address_prefixes                              = ["10.0.16.0/20"]
          private_endpoint_network_policies_enabled     = true
          private_link_service_network_policies_enabled = false
        },
        {
          name                                          = "PodSubnet"
          address_prefixes                              = ["10.0.32.0/20"]
          private_endpoint_network_policies_enabled     = true
          private_link_service_network_policies_enabled = false
        },
        {
          name                                          = "DevXGeneralSubnet"
          address_prefixes                              = ["10.0.48.0/20"]
          private_endpoint_network_policies_enabled     = true
          private_link_service_network_policies_enabled = false
        }
      ]
    }
  }
  type = map(any)
}

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

variable "aks_cluster_name" {
  description = "(Required) Specifies the name of the AKS cluster."
  default     = "DevXAks"
  type        = string
}

variable "aks_private_cluster" {
  type    = bool
  default = true
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
  description = "(Required) Specifies the SSH public key for the jumpbox virtual machine and AKS worker nodes."
  type        = string
  default     = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCzkaoqP5dPnw+9p2mwo2ZVkft970st3sd0PmTV/Q4kKVCmPE3PilwSMN3ryWGuSUqkWUXkOypFMw83DU06HwvOv2o+KJxMUZRSswaHbpU4HmjGlK8zkQAz0IRGOCcW+CiLnNbVgjq7jB6ESD9yRU4XhmEb1TGt7wmQgKkWqR1hmsd0jDCzQHHztuWbeipjeNsJhpSMzJD9iv7/tdPrnBABZ4/4mS9h8NfOVokbXVcgG30qZM6RHH0PUiWaem5ntA2WXHjjTa2oGDPy3p4jC+O8C2yXY7VgqN5cGSmmIpBGc9qrZhDNx+1ZtGOUp8fEotZ5KHtzPmPqdvz86Fq45y2j mikhailkhviadchenia@Mikhails-MBP"
}

variable "workload_identity_enabled" {
  description = "(Optional) Specifies whether Azure AD Workload Identity should be enabled for the Cluster. Defaults to false."
  type        = bool
  default     = false
}

/**
 * Storage account variables
 */
variable "storage_account_prefix" {
  type    = string
  default = "boot"
}

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
    "AcrPrivate"      = "privatelink.azurecr.io",
    "KeyVaultPrivate" = "privatelink.vaultcore.azure.net",
    "BlobPrivate"     = "privatelink.blob.core.windows.net"
  }
}

###################################################################################################################

variable "additional_node_pool_name" {
  description = "(Required) Specifies the name of the node pool."
  type        = string
  default     = "user"
}

variable "additional_node_pool_vm_size" {
  description = "(Required) The SKU which should be used for the Virtual Machines used in this Node Pool. Changing this forces a new resource to be created."
  type        = string
  default     = "Standard_B2s"
}

variable "additional_node_pool_availability_zones" {
  description = "(Optional) A list of Availability Zones where the Nodes in this Node Pool should be created in. Changing this forces a new resource to be created."
  type        = list(string)
  default     = ["2", "3"]
}

variable "additional_node_pool_enable_auto_scaling" {
  description = "(Optional) Whether to enable auto-scaler. Defaults to false."
  type        = bool
  default     = true
}

variable "additional_node_pool_enable_host_encryption" {
  description = "(Optional) Should the nodes in this Node Pool have host encryption enabled? Defaults to false."
  type        = bool
  default     = false
}

variable "additional_node_pool_enable_node_public_ip" {
  description = "(Optional) Should each node have a Public IP Address? Defaults to false. Changing this forces a new resource to be created."
  type        = bool
  default     = false
}

variable "additional_node_pool_max_pods" {
  description = "(Optional) The maximum number of pods that can run on each agent. Changing this forces a new resource to be created."
  type        = number
  default     = 50
}

variable "additional_node_pool_mode" {
  description = "(Optional) Should this Node Pool be used for System or User resources? Possible values are System and User. Defaults to User."
  type        = string
  default     = "User"
}

variable "additional_node_pool_node_labels" {
  description = "(Optional) A list of Kubernetes taints which should be applied to nodes in the agent pool (e.g key=value:NoSchedule). Changing this forces a new resource to be created."
  type        = map(any)
  default     = {}
}

variable "additional_node_pool_node_taints" {
  description = "(Optional) A map of Kubernetes labels which should be applied to nodes in this Node Pool. Changing this forces a new resource to be created."
  type        = list(string)
  default     = ["CriticalAddonsOnly=true:NoSchedule"]
}

variable "additional_node_pool_os_disk_type" {
  description = "(Optional) The type of disk which should be used for the Operating System. Possible values are Ephemeral and Managed. Defaults to Managed. Changing this forces a new resource to be created."
  type        = string
  default     = "Managed"
}

variable "additional_node_pool_os_type" {
  description = "(Optional) The Operating System which should be used for this Node Pool. Changing this forces a new resource to be created. Possible values are Linux and Windows. Defaults to Linux."
  type        = string
  default     = "Linux"
}

variable "additional_node_pool_priority" {
  description = "(Optional) The Priority for Virtual Machines within the Virtual Machine Scale Set that powers this Node Pool. Possible values are Regular and Spot. Defaults to Regular. Changing this forces a new resource to be created."
  type        = string
  default     = "Regular"
}

variable "additional_node_pool_max_count" {
  description = "(Required) The maximum number of nodes which should exist within this Node Pool. Valid values are between 0 and 1000 and must be greater than or equal to min_count."
  type        = number
  default     = 0
}

variable "additional_node_pool_min_count" {
  description = "(Required) The minimum number of nodes which should exist within this Node Pool. Valid values are between 0 and 1000 and must be less than or equal to max_count."
  type        = number
  default     = 0
}

variable "additional_node_pool_node_count" {
  description = "(Optional) The initial number of nodes which should exist within this Node Pool. Valid values are between 0 and 1000 and must be a value in the range min_count - max_count."
  type        = number
  default     = 0
}

variable "acr_name" {
  description = "Specifies the name of the container registry"
  type        = string
  default     = "DevXAcr"
}

variable "acr_sku" {
  description = "Specifies the name of the container registry"
  type        = string
  default     = "Premium"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "The container registry sku is invalid."
  }
}

variable "acr_admin_enabled" {
  description = "Specifies whether admin is enabled for the container registry"
  type        = bool
  default     = true
}

variable "acr_georeplication_locations" {
  description = "(Optional) A list of Azure locations where the container registry should be geo-replicated."
  type        = list(string)
  default     = []
}

variable "bastion_host_name" {
  description = "(Optional) Specifies the name of the bastion host"
  default     = "DevXBastionHost"
  type        = string
}


