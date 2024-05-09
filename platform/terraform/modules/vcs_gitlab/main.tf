terraform {

  required_providers {
    gitlab = {
      # https://registry.terraform.io/providers/gitlabhq/gitlab/latest/docs
      source  = "gitlabhq/gitlab"
      version = "<GITLAB_PROVIDER_VERSION>"
    }
  }
}

data "gitlab_group" "owner" {
  full_path = var.vcs_owner
}
