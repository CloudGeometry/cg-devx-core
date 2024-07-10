resource "gitlab_user_runner" "group_runner" {
  runner_type = "group_type"
  group_id    = data.gitlab_group.owner.group_id
}
