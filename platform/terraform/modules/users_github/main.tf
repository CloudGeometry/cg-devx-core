terraform {

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 5.17.0"
    }
    vault = {
      source = "hashicorp/vault"
    }
  }
}
