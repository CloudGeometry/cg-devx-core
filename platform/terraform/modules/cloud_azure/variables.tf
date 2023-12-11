variable "region" {
  type        = string
  default     = "westeurope"
  description = "Specifies the location for the resource group and all the resources"
}

variable "cluster_network_cidr" {
  type    = string
  default = "10.1.0.0/16"
  validation {
    condition     = can(cidrnetmask(var.cluster_network_cidr))
    error_message = "Must be a valid IPv4 CIDR block address."
  }
}

variable "az_count" {
  type    = number
  default = 1
  validation {
    condition     = var.az_count > 0
    error_message = "Must be > 0"
  }
}

variable "cluster_name" {
  type        = string
  default     = "CGDevX"
  description = "(Required) Specifies the name of the AKS cluster."
  validation {
    condition     = (length(var.cluster_name) <= 16) && (length(var.cluster_name) >= 2)
    error_message = "Must be between 2 and 16 symbols long"
  }
}

variable "cluster_version" {
  type        = string
  default     = "1.27"
  description = "(Optional) Specifies the AKS Kubernetes version"
}

variable "node_groups" {
  type = list(object({
    name           = optional(string, "default")
    instance_types = optional(list(string), ["Standard_B2ms"])
    capacity_type  = optional(string, "Regular")
    min_size       = optional(number, 3)
    max_size       = optional(number, 5)
    desired_size   = optional(number, 3)
  }))
  default = [
    {
      name           = "default"
      instance_types = ["Standard_B2ms"]
      capacity_type  = "on_demand"
      min_size       = 3
      max_size       = 5
      desired_size   = 3
    }
  ]
}

variable "cluster_node_labels" {
  type    = map(string)
  default = {
    ProvisionedBy = "CGDevX"
  }
  description = "(Optional) Specifies the AKS node labels"
}

variable "alert_emails" {
  type    = list(string)
  default = []
}

variable "ssh_public_key" {
  description = "(Required) Specifies the SSH public key for AKS worker nodes."
  type        = string
  default     = ""
}
