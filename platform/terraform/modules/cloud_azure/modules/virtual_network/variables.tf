variable "resource_group_name" {
  description = "Resource Group name"
  type        = string
}

variable "region" {
  description = "Location in which to deploy the network"
  type        = string
}

variable "vnet_name" {
  description = "Specifies the name of the hub virtual virtual network"
  type        = string
}

variable "address_space" {
  description = "Specifies the address space of the hub virtual virtual network"
  type        = list(string)
}

variable "subnets" {
  description = "Subnets configuration"
  type = list(object({
    name                                          = string
    address_prefixes                              = list(string)
    private_endpoint_network_policies_enabled     = bool
    private_link_service_network_policies_enabled = bool
  }))
}

variable "tags" {
  description = "(Optional) Specifies the tags of the storage account"
  default     = {}
}

variable "log_analytics_workspace_id" {
  description = "Specifies the log analytics workspace id"
  type        = string
}

variable "log_analytics_retention_days" {
  description = "Specifies the number of days of the retention policy"
  type        = number
  default     = 7
}

# variable "hub_firewall_subnet_address_prefix" {
#   description = "Specifies the address prefix of the firewall subnet"
#   default     = ["10.1.0.0/24"]
#   type        = list(string)
# }

# variable "hub_bastion_subnet_address_prefix" {
#   description = "Specifies the address prefix of the firewall subnet"
#   default     = ["10.1.1.0/24"]
#   type        = list(string)
# }

# variable "aks_vnet_name" {
#   description = "Specifies the name of the AKS subnet"
#   default     = "DevXAksVNet"
#   type        = string
# }

# variable "aks_vnet_address_space" {
#   description = "Specifies the address prefix of the AKS subnet"
#   default     =  ["10.0.0.0/16"]
#   type        = list(string)
# }

# variable "vm_subnet_name" {
#   description = "Specifies the name of the jumpbox subnet"
#   default     = "DevXGeneralSubnet"
#   type        = string
# } 

# variable "vm_subnet_address_prefix" {
#   description = "Specifies the address prefix of the jumbox subnet"
#   default     = ["10.0.48.0/20"]
#   type        = list(string)
# }

