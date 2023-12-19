# harbor output
output "main_robot_full_name" {
  value = resource.harbor_robot_account.main.full_name
}

output "dockerhub_proxy_name" {
  value = harbor_project.proxy.name
}
