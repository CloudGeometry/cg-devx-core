output "robot_user_pass" {
  value = resource.random_password.password.result
  sensitive = true
}