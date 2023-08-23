resource "github_user_ssh_key" "vcs-bot" {
  title = "vcs-bot"
  key   = var.vcs_bot_ssh_public_key
}