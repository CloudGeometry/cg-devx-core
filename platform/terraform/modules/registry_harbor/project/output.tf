output "workload_robot_full_name" {
  value     = resource.harbor_robot_account.workload_robot.full_name
  sensitive = true
}

output "workload_robot_pass" {
  value     = resource.random_password.robot_password.result
  sensitive = true
}