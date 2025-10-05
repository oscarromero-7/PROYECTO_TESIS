
# Código generado automáticamente por OptiMon - Docker Local
# Versión: 16
# Fecha: 2025-10-05T14:16:25.309918

terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "npipe:////.//pipe//docker_engine"  # Windows
  # host = "unix:///var/run/docker.sock"    # Linux/Mac
}

# Recrear contenedores detectados

resource "docker_container" "optimon_alertmanager" {
  name  = "optimon_alertmanager"
  image = "prom/alertmanager:latest"
  
  
  
  restart = "unless-stopped"
  
  labels {
    label = "optimon.generated"
    value = "true"
  }
}

resource "docker_container" "optimon_prometheus" {
  name  = "optimon_prometheus"
  image = "prom/prometheus:latest"
  
  
  ports {
    internal = 9090
    external = 9090
  }
  
  
  restart = "unless-stopped"
  
  labels {
    label = "optimon.generated"
    value = "true"
  }
}

resource "docker_container" "optimon_grafana" {
  name  = "optimon_grafana"
  image = "grafana/grafana:latest"
  
  
  ports {
    internal = 3000
    external = 3000
  }
  
  
  restart = "unless-stopped"
  
  labels {
    label = "optimon.generated"
    value = "true"
  }
}


# Output de las especificaciones del sistema
output "system_specs" {
  value = {
    cpu_cores  = 12
    memory_gb  = 15.71
    disk_gb    = 457.61
  }
}