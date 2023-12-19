# harbor output
output "dockerhub_proxy_name" {
  value = module.registry.dockerhub_proxy_name
}
output "gcr_proxy_name" {
  value = module.registry.gcr_proxy_name
}
output "k8s_gcr_proxy_name" {
  value = module.registry.k8s_gcr_proxy_name
}
output "quay_proxy_name" {
  value = module.registry.quay_proxy_name
}
