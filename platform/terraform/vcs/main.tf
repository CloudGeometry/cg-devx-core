terraform {
 
  ## 
  #   backend "s3" {
  #     bucket = ""
  #     key    = "terraform/github/terraform.tfstate"

  #     region  = ""
  #     encrypt = true
  #   }

}

# Configure the GitHub Provider
provider "github" {}


# Variables for templating
# - `<GIT_PROVIDER>` - git-provider
# - `<GIT_ORGANIZATION_NAME>` - git-org
# - `<GIT_ACCESS_TOKEN>` - git-access-token
# - `<GIT_REPOSITORY_NAME>` - gitops-repo-name
# - `<ATLANTIS_INGRESS_URL>` Note!: URL does not contain protocol suffix
# - `<VCS_BOT_SSH_PUBLIC_KEY>`


module "vcs" {
  source = "../modules/vcs_github"

  gitops_repo_name             = "gitops-repository"  #set <GIT_REPOSITORY_NAME> here 
  atlantis_url                 = "https://atlantis.cgdevx-demo.demoapps.click/events" # set "https://<ATLANTIS_INGRESS_URL>/events"
  atlantis_repo_webhook_secret = var.atlantis_repo_webhook_secret
  vcs_bot_ssh_public_key       = var.vcs_bot_ssh_public_key

}

# module "vcs" {
#   source = "../modules/vcs_<GIT_PROVIDER>"

#   gitops_repo_name             = "<GITOPS_REPOSITORY_NAME>"
#   atlantis_url                 = "https://<ATLANTIS_INGRESS_URL>/events"
# #  secrets variables need to define through environment variables:
# #  export TF_VAR_atlantis_repo_webhook_secret="<ATLANTIS_WEBHOOK_SECRET>"
# #  export TF_VAR_vcs_bot_ssh_public_key="<VCS_BOT_SSH_PUBLIC_KEY"
# #  github provider authentification passed by env variables
# #  export GITHUB_TOKEN="<GIT_ACCESS_TOKEN>"
# #  export GITHUB_OWNER="<GIT_ORGANIZATION_NAME>"

# }

