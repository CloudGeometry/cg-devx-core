variable "vcs_bot_ssh_public_key" {
  description = "public key for git operations"
  type        = string
  default     = ""
}

variable "vcs_bot_ssh_private_key" {
  description = "private key for git operations"
  default     = ""
  type        = string
  sensitive   = true
}

variable "vcs_token" {
  description = "token for git operations"
  default     = ""
  type        = string
  sensitive   = true
}

variable "atlantis_repo_webhook_secret" {
  description = "atlantis webhook secret"
  default     = ""
  type        = string
  sensitive   = true
}

variable "atlantis_repo_webhook_url" {
  description = "atlantis webhook url"
  default     = ""
  type        = string
}

variable "argocd_webhook_secret" {
  description = "argocd webhook secret"
  default     = ""
  type        = string
  sensitive   = true
}

variable "vault_token" {
  description = "vault token"
  default     = ""
  type        = string
  sensitive   = true
}

variable "cluster_endpoint" {
  description = "(Required) K8s cluster endpoint"
  type        = string
}

variable "workloads" {
  description = "Workloads configuration"
  type        = map(object({
    description = optional(string, "")
  }))
  default = {}
}

variable "cluster_ssh_public_key" {
  description = "Specifies the SSH public key for K8s worker nodes. Only applicable to AKS."
  type        = string
  default     = ""
}

variable "tf_backend_storage_access_key" {
  description = "Specifies the access key for tf backend storage. Only applicable to AKS."
  type        = string
  default     = ""
}
