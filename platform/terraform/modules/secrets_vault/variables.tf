variable "cluster_name" {
  description = "primary cluster name"
  default     = ""
  type        = string

}

variable "vcs_token" {
  description = "token for git operations"
  default     = ""
  type        = string
  sensitive   = true
}

variable "vcs_bot_ssh_private_key" {
  description = "private key for git operations"
  default     = ""
  type        = string
  sensitive   = true
}

variable "vcs_bot_ssh_public_key" {
  description = "public key for git operations"
  default     = ""
  type        = string
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

variable "cd_webhook_secret" {
  description = "cd webhook secret"
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

variable "workloads" {
  description = "workloads vault configuration"
  type        = map(object({
    description = optional(string, "")
  }))
  default = {}
}

variable "cluster_endpoint" {
  description = "(Required) K8s cluster endpoint"
  type        = string
}

variable "cluster_ssh_public_key" {
  description = "Specifies the SSH public key for K8s worker nodes. Only applicable to AKS."
  type        = string
  default     = null
}

variable "tf_backend_storage_access_key" {
  description = "Specifies the access key for tf backend storage. Only applicable to AKS."
  type        = string
  default     = ""
}

variable "cloud_binary_artifacts_store_access_key" {
  description = "Specifies the access key for CI artifact store backend storage. Only applicable to AKS."
  type        = string
  default     = ""
}

variable "image_registry_auth" {
  description = "Specifies the access keys for image registries"
  type        = map(object({login = string, token = string}))
  default     = {}
}
