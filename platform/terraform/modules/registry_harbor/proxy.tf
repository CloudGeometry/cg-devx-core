resource "harbor_project" "proxy" {
  name        = "dockerhub-proxy"
  registry_id = harbor_registry.docker.registry_id
}

resource "harbor_registry" "docker" {
  provider_name = "docker-hub"
  name          = "dockerhub-proxy"
  endpoint_url  = "https://hub.docker.com"
}