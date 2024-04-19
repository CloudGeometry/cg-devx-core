terraform {

  required_providers {
    gitlab = {
      source = "gitlabhq/gitlab"
      version = "<GITLAB_PROVIDER_VERSION>"
    }
    vault = {
      source = "hashicorp/vault"
    }
  }
}
