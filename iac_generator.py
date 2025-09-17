#!/usr/bin/env python3
"""
Generador de IaC (Terraform/Ansible) basado en infraestructura existente
Para el proyecto OptiMon - Sistema de Recomendaciones con IaC para Pymes
"""

import json
import os
import boto3
import requests
from datetime import datetime
import subprocess
from jinja2 import Template

class IaCGenerator:
    def __init__(self):
        self.output_dir = "3-CODIGO-GENERADO"
        self.version = self._get_next_version()
        self.scan_results = {}

    def _get_next_version(self):
        """Obtiene el siguiente número de versión disponible"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        versions = [d for d in os.listdir(self.output_dir) if d.startswith('version_')]
        if not versions:
            return 1
        latest = max([int(v.split('_')[1]) for v in versions])
        return latest + 1

    def scan_local_infrastructure(self):
        """Escanea la infraestructura local (Docker, sistema)"""
        print("[INFO] Escaneando infraestructura local...")

        local_info = {
            'type': 'local',
            'containers': self._get_docker_containers(),
            'system_specs': self._get_system_specs(),
            'services': self._get_running_services()
        }

        self.scan_results['local'] = local_info
        return local_info

    def scan_aws_infrastructure(self):
        """Escanea infraestructura AWS existente"""
        print("[INFO] Escaneando infraestructura AWS...")

        try:
            ec2 = boto3.client('ec2')

            # Obtener instancias
            instances = ec2.describe_instances()

            aws_info = {
                'type': 'aws',
                'instances': [],
                'vpcs': [],
                'security_groups': []
            }

            # Procesar instancias
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    if instance['State']['Name'] != 'terminated':
                        aws_info['instances'].append({
                            'instance_id': instance['InstanceId'],
                            'instance_type': instance['InstanceType'],
                            'state': instance['State']['Name'],
                            'vpc_id': instance.get('VpcId', ''),
                            'subnet_id': instance.get('SubnetId', ''),
                            'security_groups': [sg['GroupId'] for sg in instance.get('SecurityGroups', [])]
                        })

            # Obtener VPCs
            vpcs = ec2.describe_vpcs()
            for vpc in vpcs['Vpcs']:
                aws_info['vpcs'].append({
                    'vpc_id': vpc['VpcId'],
                    'cidr_block': vpc['CidrBlock'],
                    'is_default': vpc['IsDefault']
                })

            self.scan_results['aws'] = aws_info
            return aws_info

        except Exception as e:
            print(f"[ERROR] Error escaneando AWS: {e}")
            return None

    def scan_azure_infrastructure(self):
        """Escanea infraestructura Azure existente"""
        print("[INFO] Escaneando infraestructura Azure...")

        try:
            # Ejecutar Azure CLI para obtener VMs
            result = subprocess.run(['az', 'vm', 'list', '--output', 'json'],
                                  capture_output=True, text=True, check=True)

            vms = json.loads(result.stdout)

            azure_info = {
                'type': 'azure',
                'virtual_machines': []
            }

            for vm in vms:
                azure_info['virtual_machines'].append({
                    'name': vm['name'],
                    'resource_group': vm['resourceGroup'],
                    'location': vm['location'],
                    'vm_size': vm['hardwareProfile']['vmSize'],
                    'os_type': vm['storageProfile']['osDisk']['osType']
                })

            self.scan_results['azure'] = azure_info
            return azure_info

        except Exception as e:
            print(f"[ERROR] Error escaneando Azure: {e}")
            return None

    def _get_docker_containers(self):
        """Obtiene información de contenedores Docker"""
        try:
            result = subprocess.run(['docker', 'ps', '--format', 'json'],
                                  capture_output=True, text=True, check=True)

            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    container = json.loads(line)
                    containers.append({
                        'name': container['Names'],
                        'image': container['Image'],
                        'ports': container['Ports'],
                        'status': container['Status']
                    })
            return containers
        except:
            return []

    def _get_system_specs(self):
        """Obtiene especificaciones del sistema"""
        import psutil

        return {
            'cpu_cores': psutil.cpu_count(),
            'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_gb': round(psutil.disk_usage('/').total / (1024**3), 2)
        }

    def _get_running_services(self):
        """Obtiene servicios en ejecución (básico)"""
        # Simplificado para la demo
        return ['prometheus', 'grafana', 'node_exporter']

    def generate_terraform_code(self):
        """Genera código Terraform basado en los escaneos"""
        print(f"[INFO] Generando código Terraform versión {self.version}...")

        version_dir = os.path.join(self.output_dir, f"version_{self.version}")
        terraform_dir = os.path.join(version_dir, "terraform")
        os.makedirs(terraform_dir, exist_ok=True)

        # Template para AWS
        if 'aws' in self.scan_results:
            self._generate_aws_terraform(terraform_dir)

        # Template para Azure
        if 'azure' in self.scan_results:
            self._generate_azure_terraform(terraform_dir)

        # Template para local/Docker
        if 'local' in self.scan_results:
            self._generate_docker_terraform(terraform_dir)

        print(f"[OK] Código Terraform generado en: {terraform_dir}")

    def _generate_aws_terraform(self, output_dir):
        """Genera código Terraform para AWS"""
        aws_template = Template('''
# Código generado automáticamente por OptiMon
# Versión: {{ version }}
# Fecha: {{ timestamp }}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

{% for instance in instances %}
resource "aws_instance" "instance_{{ loop.index }}" {
  ami           = "ami-0c02fb55956c7d316" # Amazon Linux 2023
  instance_type = "{{ instance.instance_type }}"
  
  {% if instance.subnet_id %}
  subnet_id = "{{ instance.subnet_id }}"
  {% endif %}
  
  vpc_security_group_ids = [
    {% for sg in instance.security_groups %}
    "{{ sg }}",
    {% endfor %}
  ]
  
  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    
    # Instalar Node Exporter para monitoreo
    wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-1.6.1.linux-amd64.tar.gz
    tar xzf node_exporter-1.6.1.linux-amd64.tar.gz
    sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
    
    # Crear servicio systemd
    sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOL
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=ec2-user
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOL
    
    sudo systemctl daemon-reload
    sudo systemctl enable node_exporter
    sudo systemctl start node_exporter
  EOF
  
  tags = {
    Name = "OptiMon-Instance-{{ loop.index }}"
    Environment = "monitoring"
    GeneratedBy = "OptiMon-IaC-Generator"
  }
}
{% endfor %}

# Variables
variable "aws_region" {
  description = "Región AWS"
  type        = string
  default     = "us-east-1"
}

# Outputs
{% for instance in instances %}
output "instance_{{ loop.index }}_public_ip" {
  value = aws_instance.instance_{{ loop.index }}.public_ip
}

output "instance_{{ loop.index }}_private_ip" {
  value = aws_instance.instance_{{ loop.index }}.private_ip
}
{% endfor %}
''')
        
        aws_data = self.scan_results['aws']
        rendered = aws_template.render(
            version=self.version,
            timestamp=datetime.now().isoformat(),
            instances=aws_data['instances']
        )
        
        with open(os.path.join(output_dir, 'aws_infrastructure.tf'), 'w') as f:
            f.write(rendered)

    def _generate_azure_terraform(self, output_dir):
        """Genera código Terraform para Azure"""
        azure_template = Template('''
# Código generado automáticamente por OptiMon - Azure
# Versión: {{ version }}
# Fecha: {{ timestamp }}

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "optimon_rg" {
  name     = "optimon-monitoring-rg"
  location = var.azure_location
}

{% for vm in virtual_machines %}
resource "azurerm_virtual_machine" "vm_{{ loop.index }}" {
  name                = "{{ vm.name }}"
  location            = azurerm_resource_group.optimon_rg.location
  resource_group_name = azurerm_resource_group.optimon_rg.name
  vm_size             = "{{ vm.vm_size }}"
  
  storage_os_disk {
    name              = "{{ vm.name }}-osdisk"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }
  
  storage_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }
  
  os_profile {
    computer_name  = "{{ vm.name }}"
    admin_username = "azureuser"
    custom_data    = base64encode(<<-EOF
      #!/bin/bash
      apt-get update -y
      
      # Instalar Node Exporter
      wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-1.6.1.linux-amd64.tar.gz
      tar xzf node_exporter-1.6.1.linux-amd64.tar.gz
      sudo cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
      
      # Crear servicio systemd
      sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOL
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=azureuser
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOL
      
      sudo systemctl daemon-reload
      sudo systemctl enable node_exporter
      sudo systemctl start node_exporter
    EOF
    )
  }
  
  os_profile_linux_config {
    disable_password_authentication = false
  }
  
  tags = {
    Environment = "monitoring"
    GeneratedBy = "OptiMon-IaC-Generator"
  }
}
{% endfor %}

variable "azure_location" {
  description = "Ubicación Azure"
  type        = string
  default     = "East US"
}
''')
        
        azure_data = self.scan_results['azure']
        rendered = azure_template.render(
            version=self.version,
            timestamp=datetime.now().isoformat(),
            virtual_machines=azure_data['virtual_machines']
        )
        
        with open(os.path.join(output_dir, 'azure_infrastructure.tf'), 'w') as f:
            f.write(rendered)

    def _generate_docker_terraform(self, output_dir):
        """Genera código Terraform para contenedores Docker locales"""
        docker_template = Template('''
# Código generado automáticamente por OptiMon - Docker Local
# Versión: {{ version }}
# Fecha: {{ timestamp }}

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
{% for container in containers %}
resource "docker_container" "{{ container.name | replace('-', '_') }}" {
  name  = "{{ container.name }}"
  image = "{{ container.image }}"
  
  {% if 'prometheus' in container.name %}
  ports {
    internal = 9090
    external = 9090
  }
  {% elif 'grafana' in container.name %}
  ports {
    internal = 3000
    external = 3000
  }
  {% elif 'node_exporter' in container.name %}
  ports {
    internal = 9100
    external = 9100
  }
  {% elif 'windows_exporter' in container.name %}
  ports {
    internal = 9182
    external = 9182
  }
  {% endif %}
  
  restart = "unless-stopped"
  
  labels {
    label = "optimon.generated"
    value = "true"
  }
}
{% endfor %}

# Output de las especificaciones del sistema
output "system_specs" {
  value = {
    cpu_cores  = {{ system_specs.cpu_cores }}
    memory_gb  = {{ system_specs.memory_gb }}
    disk_gb    = {{ system_specs.disk_gb }}
  }
}
''')
        
        local_data = self.scan_results['local']
        rendered = docker_template.render(
            version=self.version,
            timestamp=datetime.now().isoformat(),
            containers=local_data['containers'],
            system_specs=local_data['system_specs']
        )
        
        with open(os.path.join(output_dir, 'docker_infrastructure.tf'), 'w') as f:
            f.write(rendered)

    def generate_ansible_playbooks(self):
        """Genera playbooks de Ansible para configuración"""
        print(f"[INFO] Generando playbooks Ansible versión {self.version}...")

        version_dir = os.path.join(self.output_dir, f"version_{self.version}")
        ansible_dir = os.path.join(version_dir, "ansible")
        os.makedirs(ansible_dir, exist_ok=True)

        # Generar playbook de monitoreo
        monitoring_playbook = '''---
- name: Configurar Node Exporter para monitoreo OptiMon
  hosts: all
  become: yes
  
  tasks:
    - name: Descargar Node Exporter
      get_url:
        url: "https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-1.6.1.linux-amd64.tar.gz"
        dest: "/tmp/node_exporter.tar.gz"
    
    - name: Extraer Node Exporter
      unarchive:
        src: "/tmp/node_exporter.tar.gz"
        dest: "/tmp"
        remote_src: yes
    
    - name: Copiar binario
      copy:
        src: "/tmp/node_exporter-1.6.1.linux-amd64/node_exporter"
        dest: "/usr/local/bin/node_exporter"
        mode: '0755'
        remote_src: yes
    
    - name: Crear servicio systemd
      systemd:
        name: node_exporter
        state: started
        enabled: yes
        daemon_reload: yes
        
    - name: Abrir puerto 9100 (firewall)
      ufw:
        rule: allow
        port: 9100
        proto: tcp
      ignore_errors: yes
'''

        with open(os.path.join(ansible_dir, 'setup_monitoring.yml'), 'w') as f:
            f.write(monitoring_playbook)

        print(f"[OK] Playbooks Ansible generados en: {ansible_dir}")

    def save_scan_results(self):
        """Guarda los resultados del escaneo para referencia"""
        version_dir = os.path.join(self.output_dir, f"version_{self.version}")
        os.makedirs(version_dir, exist_ok=True)

        scan_file = os.path.join(version_dir, 'scan_results.json')

        with open(scan_file, 'w') as f:
            json.dump(self.scan_results, f, indent=2, default=str)

        print(f"[OK] Resultados del escaneo guardados en: {scan_file}")

    def generate_summary_report(self):
        """Genera un reporte resumen de la infraestructura"""
        version_dir = os.path.join(self.output_dir, f"version_{self.version}")

        report = f"""
# Reporte de Infraestructura OptiMon
**Versión:** {self.version}  
**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Resumen de Infraestructura Detectada

"""
        
        if 'local' in self.scan_results:
            local = self.scan_results['local']
            report += f"""
### Servidor Local
- **CPU Cores:** {local['system_specs']['cpu_cores']}
- **Memoria:** {local['system_specs']['memory_gb']} GB
- **Disco:** {local['system_specs']['disk_gb']} GB
- **Contenedores Docker:** {len(local['containers'])}

"""
        
        if 'aws' in self.scan_results:
            aws = self.scan_results['aws']
            report += f"""
### Infraestructura AWS
- **Instancias EC2:** {len(aws['instances'])}
- **VPCs:** {len(aws['vpcs'])}
- **Security Groups:** {len(aws['security_groups'])}

"""
        
        if 'azure' in self.scan_results:
            azure = self.scan_results['azure']
            report += f"""
### Infraestructura Azure
- **Máquinas Virtuales:** {len(azure['virtual_machines'])}

"""
        
        report += f"""
## Archivos Generados
- `terraform/` - Código Terraform para replicar la infraestructura
- `ansible/` - Playbooks para configuración automatizada
- `scan_results.json` - Datos completos del escaneo

## Cómo usar el código generado
1. `cd {version_dir}/terraform`
2. `terraform init`
3. `terraform plan`
4. `terraform apply`

## Monitoreo
Los recursos incluyen configuración automática de Node Exporter para integración con OptiMon.
"""
        
        with open(os.path.join(version_dir, 'README.md'), 'w') as f:
            f.write(report)
        
        print(f"[OK] Reporte generado: {os.path.join(version_dir, 'README.md')}")

def main():
    """Función principal del generador"""
    print("=== OptiMon IaC Generator ===")
    print("Generando código Infrastructure-as-Code basado en infraestructura existente...")
    print()

    generator = IaCGenerator()

    # Escanear según el tipo de infraestructura disponible
    print("Selecciona qué escanear:")
    print("[1] Solo local (Docker/sistema)")
    print("[2] AWS + Local")
    print("[3] Azure + Local")
    print("[4] Todo (AWS + Azure + Local)")

    option = input("Opción: ").strip()

    if option in ['1', '2', '3', '4']:
        # Escaneo local siempre
        generator.scan_local_infrastructure()

        if option in ['2', '4']:
            generator.scan_aws_infrastructure()

        if option in ['3', '4']:
            generator.scan_azure_infrastructure()

        # Generar código
        generator.generate_terraform_code()
        generator.generate_ansible_playbooks()
        generator.save_scan_results()
        generator.generate_summary_report()

        print(f"\n✅ Código IaC generado exitosamente!")
        print(f"📁 Ubicación: {os.path.join(generator.output_dir, f'version_{generator.version}')}")
        print(f"📊 Versión: {generator.version}")
    else:
        print("Opción inválida")

if __name__ == "__main__":
    main()