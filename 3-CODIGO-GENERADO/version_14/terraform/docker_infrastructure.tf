
# Código generado automáticamente por OptiMon - Docker Local
# Versión: 14
# Fecha: 2025-10-05T13:31:02.553358

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


# Output de las especificaciones del sistema
output "system_specs" {
  value = {
    cpu_cores  = 12
    memory_gb  = 15.71
    disk_gb    = 457.61
  }
}