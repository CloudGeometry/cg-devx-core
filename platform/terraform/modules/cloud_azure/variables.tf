variable "region" {
  description = "Specifies the location for the resource group and all the resources"
  default     = "westeurope"
  type        = string
}

variable "cluster_network_cidr" {
  type    = string
  default = "10.1.0.0/16"
}

variable "az_count" {
  type    = number
  default = 1
  validation {
    condition     = var.az_count > 0
    error_message = "az_count must be > 0"
  }
}

variable "cluster_name" {
  description = "(Required) Specifies the name of the AKS cluster."
  default     = "CGDevX"
  type        = string
}

variable "node_groups" {
  type = list(object({
    name           = optional(string, "default")
    instance_types = optional(list(string), ["Standard_B2s"])
    capacity_type  = optional(string, "Regular")
    min_size       = optional(number, 3)
    max_size       = optional(number, 5)
    desired_size   = optional(number, 3)
  }))
  default = [
    {
      name           = "default"
      instance_types = ["Standard_B2s"]
      capacity_type  = "on_demand"
      min_size       = 3
      max_size       = 5
      desired_size   = 3
    }
  ]
}

variable "alert_emails" {
  type    = list(string)
  default = []
}

variable "cluster_version" {
  description = "(Optional) Specifies the AKS Kubernetes version"
  default     = "1.27"
  type        = string
}

variable "cluster_node_labels" {
  description = "(Optional) Specifies the AKS node labels"
  type        = map(string)
  default     = {
    ProvisionedBy = "CGDevX"
  }
}
variable "ssh_public_key" {
  description = "(Required) Specifies the SSH public key for AKS worker nodes."
  type        = string
  default     = ""
}
