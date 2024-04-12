terraform {

  required_providers {
    gitlab = {
      source = "gitlabhq/gitlab"
      version = "~> 16.9.1"
    }
    vault = {
      source = "hashicorp/vault"
    }
  }
}
