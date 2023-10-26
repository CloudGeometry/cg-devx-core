
variable "cluster_network_cidr" {
  type    = string
  default = "10.0.0.0/16"
  validation {
    condition     = can(cidrnetmask(var.cluster_network_cidr))
    error_message = "Must be a valid IPv4 CIDR block address."
  }
}

variable "cluster_name" {
  type    = string
  default = "CGDevX"
  validation {
    condition     = (length(var.cluster_name) <= 16) && (length(var.cluster_name) >= 2)
    error_message = "Must be between 2 and 16 symbols long"
  }
  validation {
    condition     = !can(regex("-|_", var.cluster_name))
    error_message = "Value should no contain \"-\" and \"_\"."
  }
}

variable "cluster_version" {
  type    = string
  default = "1.27"
}

variable "ssh_public_key" {
  description = "(Optional) SSH public key to access worker nodes."
  type        = string
  default     = ""
}
