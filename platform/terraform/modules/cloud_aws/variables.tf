variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_account_id" {
  type    = string
  default = "test"
}
/*
variable "hosted_zone_name" {
  type = string
}
*/
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
  type    = string
  default = "1.27"
}

variable "node_groups" {
  type = list(object({
    name           = optional(string)
    instance_types = optional(list(string), ["t3.medium"])
    capacity_type  = optional(string, "on-demand") /*“on-demand” or “spot” */
    min_size       = optional(number, 3)
    max_size       = optional(number, 5)
    desired_size   = optional(number, 3)
    }
    )
  )
  default = [{}]
}



/*
variable "cluster_node_labels" {
  type = list(string)
}
variable "alert_emails" {
  type = list(string)
}
*/
