# docker-hub proxy
resource "harbor_project" "docker-hub-proxy" {
  name          = "dockerhub-proxy"
  registry_id   = harbor_registry.docker-hub.registry_id
  force_destroy = true
}

resource "harbor_registry" "docker-hub" {
  provider_name = "docker-hub"
  name          = "dockerhub-proxy"
  endpoint_url  = "https://hub.docker.com"
}

# gcr.io proxy
resource "harbor_project" "gcr-proxy" {
  name          = "gcr-proxy"
  registry_id   = harbor_registry.gcr.registry_id
  force_destroy = true
}

resource "harbor_registry" "gcr" {
  provider_name = "docker-registry"
  name          = "gcr-proxy"
  endpoint_url  = "https://gcr.io"
}

# k8s.gcr.io proxy
resource "harbor_project" "k8s-gcr-proxy" {
  name          = "k8s-gcr-proxy"
  registry_id   = harbor_registry.k8s-gcr.registry_id
  force_destroy = true
}

resource "harbor_registry" "k8s-gcr" {
  provider_name = "docker-registry"
  name          = "k8s-gcr-proxy"
  endpoint_url  = "https://k8s.gcr.io"
}

# quay.io proxy
resource "harbor_project" "quay-proxy" {
  name          = "quay-proxy"
  registry_id   = harbor_registry.quay.registry_id
  force_destroy = true
}

resource "harbor_registry" "quay" {
  provider_name = "quay"
  name          = "quay-proxy"
  endpoint_url  = "https://quay.io"
}