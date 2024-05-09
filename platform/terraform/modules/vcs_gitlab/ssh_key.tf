resource "gitlab_user_sshkey" "vcs-bot" {
  title = "${var.gitops_repo_name}-vcs-bot"
  key   = var.vcs_bot_ssh_public_key
}
