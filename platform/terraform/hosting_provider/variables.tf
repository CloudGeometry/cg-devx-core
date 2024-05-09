variable "cluster_ssh_public_key" {
  description = "(Optional) SSH public key to access worker nodes."
  type        = string
  default     = ""
}

variable "workloads" {
  description = "Workloads configuration"
  type        = map(object({
    description = optional(string, "")
  }))
  default = {}
}