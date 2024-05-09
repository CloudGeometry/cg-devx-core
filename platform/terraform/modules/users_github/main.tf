terraform {

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> <GITHUB_PROVIDER_VERSION>"
    }
    vault = {
      source = "hashicorp/vault"
    }
  }
}
