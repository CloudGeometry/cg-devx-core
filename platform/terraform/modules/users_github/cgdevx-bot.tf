module "cgdevx-bot" {
  # it is your automation user for all automation
  # on the platform that needs a bot account
  source = "./user"

  acl_policies      = ["admin","default"]
  email             = var.bot_email
  first_name        = "CG DevX"
  github_username   = var.vcs_bot_username
  last_name         = "Bot"
  github_team_slugs = ["${var.gitops_repo_name}-admins"]
  username          = "cgdevx-bot"
  user_disabled     = false
  userpass_accessor = data.vault_auth_backend.userpass.accessor
}
