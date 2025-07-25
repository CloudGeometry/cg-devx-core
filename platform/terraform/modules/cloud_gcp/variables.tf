variable "region" {
  type        = string
  default     = "us-central1"
  description = "Specifies the location for the resource group and all the resources"
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
  default = 1
  validation {
    condition     = var.az_count > 0
    error_message = "Must be > 0"
  }
}

variable "cluster_name" {
  type        = string
  default     = "cgdevx"
  description = "(Required) Specifies the name of the GKE cluster."
  validation {
    condition     = (length(var.cluster_name) <= 16) && (length(var.cluster_name) >= 2)
    error_message = "Must be between 2 and 16 symbols long"
  }
}

variable "cluster_version" {
  type        = string
  default     = "1.32"
  description = "(Optional) Specifies the GKE Kubernetes version"
}

variable "node_groups" {
  type = list(object({
    name           = optional(string, "default")
    instance_types = optional(list(string), ["n2-standard-2"])
    capacity_type  = optional(string, "Regular")
    min_size       = optional(number, 1)
    max_size       = optional(number, 5)
    desired_size   = optional(number, 3)
    disk_size      = optional(number, 50)
    gpu_enabled    = optional(bool, false)
  }))
  default = [
    {
      name           = "default"
      instance_types = ["n2-standard-2"]
      capacity_type  = "on_demand"
      min_size       = 1
      max_size       = 5
      desired_size   = 3
      disk_size      = 50
      gpu_enabled    = false
    }
  ]
}

variable "cluster_node_labels" {
  type    = map(string)
  default = {
    "provisioned-by" = "cg-devx"
  }
  description = "(Optional) Specifies the GKE node labels"
}

variable "tags" {
  type    = map(string)
  default = {
    "ProvisionedBy" = "CGDevX"
  }
  description = "(Optional) Specifies the GCP resource labels"
}

variable "alert_emails" {
  type    = list(string)
  default = []
}

variable "cluster_ssh_public_key" {
  description = "(Required) Specifies the SSH public key for GKE worker nodes."
  type        = string
  default     = ""
}

variable "enable_native_auto_scaling" {
  description = "Enables GKE native autoscaling feature."
  type        = bool
  default     = false
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
