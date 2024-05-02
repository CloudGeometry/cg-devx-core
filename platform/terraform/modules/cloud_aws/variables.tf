variable "region" {
  type        = string
  default     = "eu-west-1"
  description = "Specifies the regions"
}

variable "cluster_network_cidr" {
  type    = string
  default = "10.0.0.0/16"
  validation {
    condition     = can(cidrnetmask(var.cluster_network_cidr))
    error_message = "Must be a valid IPv4 CIDR block address."
  }
}

variable "az_count" {
  type    = number
  default = 3
  validation {
    condition     = var.az_count > 0
    error_message = "Must be > 0"
  }
}

variable "cluster_name" {
  type        = string
  default     = "CGDevX"
  description = "(Required) Specifies the name of the EKS cluster."
  validation {
    condition     = (length(var.cluster_name) <= 16) && (length(var.cluster_name) >= 2)
    error_message = "Must be between 2 and 16 symbols long"
  }
  validation {
    condition     = can(regex("[a-z0-9]+(?:-[a-z0-9]+)*", var.cluster_name))
    error_message = "Invalid input, string should be in kebab-case."
  }
}

variable "cluster_version" {
  type        = string
  default     = "1.29"
  description = "(Optional) Specifies the EKS Kubernetes version"
}

variable "node_group_type" {
  type    = string
  default = "EKS"
  validation {
    condition     = contains(["EKS", "SELF"], var.node_group_type)
    error_message = "Can be \"EKS\" for eks-managed  or \"SELF\" for self-managed node groups."
  }
}

variable "node_groups" {
  type = list(object({
    name           = optional(string, "default")
    instance_types = optional(list(string), ["m5.large"])
    capacity_type  = optional(string, "on_demand")
    min_size       = optional(number, 3)
    max_size       = optional(number, 6)
    desired_size   = optional(number, 4)
  }))
  default = [
    {
      name           = "default"
      instance_types = ["m5.large"]
      capacity_type  = "on_demand"
      min_size       = 3
      max_size       = 6
      desired_size   = 4
    }
  ]
}

variable "cluster_node_labels" {
  type    = map(any)
  default = {
    provisioned-by = "cg-devx"
  }
  description = "(Optional) EKS node labels"
}

variable "tags" {
  type    = map(string)
  default = {
    ProvisionedBy = "CGDevX"
  }
  description = "(Optional) Specifies the AWS resource tags"
}

variable "alert_emails" {
  type    = list(string)
  default = []
}

variable "cluster_ssh_public_key" {
  description = "(Optional) SSH public key to access worker nodes."
  type        = string
  default     = ""
}

variable "domain_name" {
  type        = string
  description = "Specifies the platform domain name"
}

variable "workloads" {
  description = "Workloads configuration"
  type        = map(object({
    description = optional(string, "")
  }))
  default = {}
}