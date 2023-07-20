variable "aws_region" {
  type = string
}

variable "aws_account_id" {
  type = string
}

variable "hosted_zone_name" {
  type = string
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
}

variable "cluster_name" {
  type    = string
  default = "gxc"
}
variable "cluster_version" {
  type = string
}

variable "node_groups" {
  type = list(object({
    }
    )
  )
}


