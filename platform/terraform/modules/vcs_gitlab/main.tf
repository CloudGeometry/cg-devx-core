terraform {

  required_providers {
    gitlab = {
      # https://registry.terraform.io/providers/gitlabhq/gitlab/latest/docs
      source  = "gitlabhq/gitlab"
      version = "16.7.0"
    }
  }
}

data "gitlab_group" "owner" {
  full_path = var.vcs_owner
}
