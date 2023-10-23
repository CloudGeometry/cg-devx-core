output "main_robot_full_name" {
  value = resource.harbor_robot_account.main.full_name
  sensitive = true
}

output "main_robot_pass" {
  value = resource.random_password.main_robot_password.result
  sensitive = true
}