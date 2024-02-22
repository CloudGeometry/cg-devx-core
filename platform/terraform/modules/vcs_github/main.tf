terraform {

  required_providers {
    github = {
      # https://registry.terraform.io/providers/integrations/github/latest/docs
      source  = "integrations/github"
      version = "~> <GITHUB_PROVIDER_VERSION>"
    }

  }
}
