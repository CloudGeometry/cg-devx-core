# harbor output
output "main_robot_full_name" {
  value = resource.harbor_robot_account.main.full_name
}

output "dockerhub_proxy_name" {
  value = harbor_project.docker-hub-proxy.name
}

output "gcr_proxy_name" {
  value = harbor_project.gcr-proxy.name
}

output "k8s_gcr_proxy_name" {
  value = harbor_project.k8s-gcr-proxy.name
}

output "quay_proxy_name" {
  value = harbor_project.quay-proxy.name
}
