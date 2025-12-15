"""
OptiMon Infrastructure as Code (IaC) Generator
Genera código de infraestructura para AWS y Azure basado en especificaciones del usuario
"""

import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class IaCGenerator:
    def __init__(self):
        self.templates_dir = Path("templates/iac")
        self.outputs_dir = Path("generated_iac")
        self.supported_providers = ["aws", "azure", "gcp"]
        self.supported_resources = {
            "aws": ["ec2", "rds", "s3", "vpc", "security_group", "load_balancer", "auto_scaling"],
            "azure": ["vm", "sql_database", "storage_account", "vnet", "nsg", "load_balancer", "vmss"],
            "gcp": ["compute_instance", "sql_instance", "storage_bucket", "vpc", "firewall", "load_balancer"]
        }
        
        # Crear directorios necesarios
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Inicializar templates de Terraform para diferentes proveedores"""
        
        # Template base AWS
        aws_main_template = '''# OptiMon Generated Infrastructure - AWS
# Generated on: {timestamp}
# Configuration: {config_name}

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region
  
  default_tags {{
    tags = {{
      Environment = var.environment
      Project     = "OptiMon"
      ManagedBy   = "OptiMon-IaC"
      CreatedOn   = "{timestamp}"
    }}
  }}
}}

# Variables
variable "aws_region" {{
  description = "AWS Region"
  type        = string
  default     = "{region}"
}}

variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "{environment}"
}}

variable "project_name" {{
  description = "Project name"
  type        = string
  default     = "{project_name}"
}}

{resources}

# Outputs
{outputs}
'''
        
        # Template base Azure
        azure_main_template = '''# OptiMon Generated Infrastructure - Azure
# Generated on: {timestamp}
# Configuration: {config_name}

terraform {{
  required_version = ">= 1.0"
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{}}
  
  subscription_id = var.subscription_id
}}

# Variables
variable "subscription_id" {{
  description = "Azure Subscription ID"
  type        = string
}}

variable "location" {{
  description = "Azure Location"
  type        = string
  default     = "{location}"
}}

variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "{environment}"
}}

variable "project_name" {{
  description = "Project name"
  type        = string
  default     = "{project_name}"
}}

# Resource Group
resource "azurerm_resource_group" "main" {{
  name     = "${{var.project_name}}-${{var.environment}}-rg"
  location = var.location
  
  tags = {{
    Environment = var.environment
    Project     = "OptiMon"
    ManagedBy   = "OptiMon-IaC"
    CreatedOn   = "{timestamp}"
  }}
}}

{resources}

# Outputs
{outputs}
'''
        
        # Guardar templates
        aws_template_path = self.templates_dir / "aws_main.tf.template"
        azure_template_path = self.templates_dir / "azure_main.tf.template"
        
        with open(aws_template_path, 'w', encoding='utf-8') as f:
            f.write(aws_main_template)
            
        with open(azure_template_path, 'w', encoding='utf-8') as f:
            f.write(azure_main_template)
    
    def generate_aws_ec2(self, config: Dict) -> str:
        """Generar recurso EC2 para AWS"""
        template = '''
# EC2 Instance - {name}
resource "aws_instance" "{resource_name}" {{
  ami                    = "{ami_id}"
  instance_type         = "{instance_type}"
  key_name              = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.{sg_name}.id]
  subnet_id             = "{subnet_id}"
  
  root_block_device {{
    volume_type = "{volume_type}"
    volume_size = {volume_size}
    encrypted   = true
  }}
  
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              {user_data}
              EOF
  
  tags = {{
    Name = "${{var.project_name}}-{name}-${{var.environment}}"
    Type = "EC2Instance"
  }}
}}

# Security Group for {name}
resource "aws_security_group" "{sg_name}" {{
  name_prefix = "${{var.project_name}}-{name}-"
  description = "Security group for {name}"
  
  {security_rules}
  
  tags = {{
    Name = "${{var.project_name}}-{name}-sg"
  }}
}}
'''
        
        # Generar reglas de seguridad
        security_rules = []
        for rule in config.get('security_rules', []):
            if rule['type'] == 'ingress':
                security_rules.append(f'''
  ingress {{
    from_port   = {rule['from_port']}
    to_port     = {rule['to_port']}
    protocol    = "{rule['protocol']}"
    cidr_blocks = ["{rule['cidr']}"]
    description = "{rule.get('description', '')}"
  }}''')
        
        return template.format(
            name=config['name'],
            resource_name=config['name'].replace('-', '_'),
            ami_id=config.get('ami_id', 'ami-0abcdef1234567890'),  # AMI por defecto
            instance_type=config.get('instance_type', 't3.micro'),
            sg_name=f"{config['name'].replace('-', '_')}_sg",
            subnet_id=config.get('subnet_id', ''),
            volume_type=config.get('volume_type', 'gp3'),
            volume_size=config.get('volume_size', 20),
            user_data=config.get('user_data', ''),
            security_rules=''.join(security_rules)
        )
    
    def generate_azure_vm(self, config: Dict) -> str:
        """Generar recurso VM para Azure"""
        template = '''
# Virtual Machine - {name}
resource "azurerm_linux_virtual_machine" "{resource_name}" {{
  name                = "${{var.project_name}}-{name}-${{var.environment}}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  size                = "{vm_size}"
  admin_username      = "adminuser"
  
  disable_password_authentication = true
  
  network_interface_ids = [
    azurerm_network_interface.{name}_nic.id,
  ]
  
  admin_ssh_key {{
    username   = "adminuser"
    public_key = var.ssh_public_key
  }}
  
  os_disk {{
    caching              = "ReadWrite"
    storage_account_type = "{disk_type}"
  }}
  
  source_image_reference {{
    publisher = "{image_publisher}"
    offer     = "{image_offer}"
    sku       = "{image_sku}"
    version   = "latest"
  }}
  
  tags = {{
    Name = "{name}"
    Type = "VirtualMachine"
  }}
}}

# Network Interface for {name}
resource "azurerm_network_interface" "{name}_nic" {{
  name                = "${{var.project_name}}-{name}-nic"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  ip_configuration {{
    name                          = "internal"
    subnet_id                     = azurerm_subnet.internal.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.{name}_pip.id
  }}
}}

# Public IP for {name}
resource "azurerm_public_ip" "{name}_pip" {{
  name                = "${{var.project_name}}-{name}-pip"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  allocation_method   = "Static"
  sku                = "Standard"
}}

# Network Security Group for {name}
resource "azurerm_network_security_group" "{name}_nsg" {{
  name                = "${{var.project_name}}-{name}-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  
  {security_rules}
}}
'''
        
        # Generar reglas de seguridad
        security_rules = []
        priority = 100
        for rule in config.get('security_rules', []):
            security_rules.append(f'''
  security_rule {{
    name                       = "{rule['name']}"
    priority                   = {priority}
    direction                  = "{rule['direction']}"
    access                     = "{rule['access']}"
    protocol                   = "{rule['protocol']}"
    source_port_range          = "*"
    destination_port_range     = "{rule['port_range']}"
    source_address_prefix      = "{rule['source']}"
    destination_address_prefix = "*"
  }}''')
            priority += 10
        
        return template.format(
            name=config['name'],
            resource_name=config['name'].replace('-', '_'),
            vm_size=config.get('vm_size', 'Standard_B1s'),
            disk_type=config.get('disk_type', 'Standard_LRS'),
            image_publisher=config.get('image_publisher', 'Canonical'),
            image_offer=config.get('image_offer', '0001-com-ubuntu-server-focal'),
            image_sku=config.get('image_sku', '20_04-lts-gen2'),
            security_rules=''.join(security_rules)
        )
    
    def generate_networking_aws(self, config: Dict) -> str:
        """Generar recursos de red para AWS"""
        template = '''
# VPC
resource "aws_vpc" "main" {{
  cidr_block           = "{vpc_cidr}"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {{
    Name = "${{var.project_name}}-vpc"
  }}
}}

# Internet Gateway
resource "aws_internet_gateway" "main" {{
  vpc_id = aws_vpc.main.id
  
  tags = {{
    Name = "${{var.project_name}}-igw"
  }}
}}

# Public Subnet
resource "aws_subnet" "public" {{
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "{public_subnet_cidr}"
  availability_zone       = "{availability_zone}"
  map_public_ip_on_launch = true
  
  tags = {{
    Name = "${{var.project_name}}-public-subnet"
    Type = "Public"
  }}
}}

# Private Subnet
resource "aws_subnet" "private" {{
  vpc_id            = aws_vpc.main.id
  cidr_block        = "{private_subnet_cidr}"
  availability_zone = "{availability_zone}"
  
  tags = {{
    Name = "${{var.project_name}}-private-subnet"
    Type = "Private"
  }}
}}

# Route Table for Public Subnet
resource "aws_route_table" "public" {{
  vpc_id = aws_vpc.main.id
  
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }}
  
  tags = {{
    Name = "${{var.project_name}}-public-rt"
  }}
}}

# Route Table Association
resource "aws_route_table_association" "public" {{
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}}
'''
        
        return template.format(
            vpc_cidr=config.get('vpc_cidr', '10.0.0.0/16'),
            public_subnet_cidr=config.get('public_subnet_cidr', '10.0.1.0/24'),
            private_subnet_cidr=config.get('private_subnet_cidr', '10.0.2.0/24'),
            availability_zone=config.get('availability_zone', 'us-west-2a')
        )
    
    def generate_networking_azure(self, config: Dict) -> str:
        """Generar recursos de red para Azure"""
        template = '''
# Virtual Network
resource "azurerm_virtual_network" "main" {{
  name                = "${{var.project_name}}-vnet"
  address_space       = ["{vnet_cidr}"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
}}

# Subnet
resource "azurerm_subnet" "internal" {{
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["{subnet_cidr}"]
}}
'''
        
        return template.format(
            vnet_cidr=config.get('vnet_cidr', '10.0.0.0/16'),
            subnet_cidr=config.get('subnet_cidr', '10.0.2.0/24')
        )
    
    def generate_infrastructure(self, config: Dict) -> Dict[str, str]:
        """Generar infraestructura completa basada en configuración"""
        
        provider = config['provider']
        project_name = config['project_name']
        environment = config.get('environment', 'dev')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generar recursos individuales
        resources = []
        outputs = []
        
        # Networking
        if config.get('include_networking', True):
            if provider == 'aws':
                resources.append(self.generate_networking_aws(config.get('networking', {})))
                outputs.append('output "vpc_id" { value = aws_vpc.main.id }')
                outputs.append('output "public_subnet_id" { value = aws_subnet.public.id }')
            elif provider == 'azure':
                resources.append(self.generate_networking_azure(config.get('networking', {})))
                outputs.append('output "vnet_id" { value = azurerm_virtual_network.main.id }')
        
        # Compute resources
        for compute_config in config.get('compute_resources', []):
            if provider == 'aws':
                resources.append(self.generate_aws_ec2(compute_config))
                outputs.append(f'output "{compute_config["name"]}_public_ip" {{ value = aws_instance.{compute_config["name"].replace("-", "_")}.public_ip }}')
            elif provider == 'azure':
                resources.append(self.generate_azure_vm(compute_config))
                outputs.append(f'output "{compute_config["name"]}_public_ip" {{ value = azurerm_public_ip.{compute_config["name"]}_pip.ip_address }}')
        
        # Variables adicionales
        additional_vars = []
        if provider == 'aws':
            additional_vars.append('''
variable "key_pair_name" {
  description = "AWS Key Pair name"
  type        = string
}''')
        elif provider == 'azure':
            additional_vars.append('''
variable "ssh_public_key" {
  description = "SSH Public Key"
  type        = string
}''')
        
        # Cargar template principal
        template_path = self.templates_dir / f"{provider}_main.tf.template"
        with open(template_path, 'r', encoding='utf-8') as f:
            main_template = f.read()
        
        # Generar archivo principal
        main_tf = main_template.format(
            timestamp=timestamp,
            config_name=config.get('name', 'OptiMon Infrastructure'),
            region=config.get('region', 'us-west-2' if provider == 'aws' else 'East US'),
            location=config.get('region', 'East US'),
            environment=environment,
            project_name=project_name,
            resources='\\n'.join(resources + additional_vars),
            outputs='\\n'.join(outputs)
        )
        
        # Generar variables.tf
        variables_tf = f'''# Variables for {project_name}
# Generated by OptiMon on {timestamp}

variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "{environment}"
}}

variable "project_name" {{
  description = "Project name"  
  type        = string
  default     = "{project_name}"
}}
'''
        
        # Generar terraform.tfvars
        tfvars = f'''# Terraform Variables for {project_name}
# Generated by OptiMon on {timestamp}

environment   = "{environment}"
project_name  = "{project_name}"
'''
        
        if provider == 'aws':
            tfvars += f'''aws_region    = "{config.get('region', 'us-west-2')}"
key_pair_name = "my-key-pair"  # Replace with your key pair name
'''
        elif provider == 'azure':
            tfvars += f'''location       = "{config.get('region', 'East US')}"
subscription_id = "your-subscription-id"  # Replace with your subscription ID
ssh_public_key  = "your-ssh-public-key"   # Replace with your SSH public key
'''
        
        # Generar README
        readme = f'''# {project_name} Infrastructure

Infrastructure as Code generated by OptiMon on {timestamp}

## Provider: {provider.upper()}

## Resources Created:
{self._generate_resource_list(config)}

## Deployment Instructions:

1. **Prerequisites:**
   - Install [Terraform](https://terraform.io/downloads.html) (>= 1.0)
   - Configure {provider.upper()} credentials

2. **Deploy:**
   ```bash
   # Initialize Terraform
   terraform init
   
   # Review the plan
   terraform plan
   
   # Apply the infrastructure
   terraform apply
   ```

3. **Configuration:**
   - Edit `terraform.tfvars` with your specific values
   - Customize resources in `main.tf` as needed

4. **Cleanup:**
   ```bash
   terraform destroy
   ```

## Cost Estimation:
Use `terraform plan` with cost estimation tools for accurate pricing.

## Security Notes:
- Review security group rules before deployment
- Use strong passwords and key pairs
- Enable encryption for storage resources
- Follow principle of least privilege

Generated by OptiMon v3.1.0-COST-OPTIMIZER
'''
        
        return {
            'main.tf': main_tf,
            'variables.tf': variables_tf,
            'terraform.tfvars': tfvars,
            'README.md': readme
        }
    
    def _generate_resource_list(self, config: Dict) -> str:
        """Generar lista de recursos para el README"""
        resources = []
        
        if config.get('include_networking'):
            if config['provider'] == 'aws':
                resources.extend([
                    "- VPC with public and private subnets",
                    "- Internet Gateway",
                    "- Route Tables"
                ])
            elif config['provider'] == 'azure':
                resources.extend([
                    "- Virtual Network (VNet)",
                    "- Subnet configuration"
                ])
        
        for compute in config.get('compute_resources', []):
            if config['provider'] == 'aws':
                resources.append(f"- EC2 Instance: {compute['name']} ({compute.get('instance_type', 't3.micro')})")
            elif config['provider'] == 'azure':
                resources.append(f"- Virtual Machine: {compute['name']} ({compute.get('vm_size', 'Standard_B1s')})")
        
        return '\\n'.join(resources) if resources else "- Basic infrastructure setup"
    
    def save_infrastructure(self, config: Dict, output_name: Optional[str] = None) -> str:
        """Guardar infraestructura generada en archivos"""
        
        if not output_name:
            output_name = f"{config['project_name']}_{config['provider']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        output_dir = self.outputs_dir / output_name
        output_dir.mkdir(exist_ok=True)
        
        # Generar archivos
        files = self.generate_infrastructure(config)
        
        # Guardar archivos
        for filename, content in files.items():
            file_path = output_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Guardar configuración original
        config_path = output_dir / 'optimon_config.json'
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return str(output_dir)
    
    def get_templates_for_provider(self, provider: str) -> Dict:
        """Obtener templates disponibles para un proveedor"""
        if provider not in self.supported_providers:
            return {}
        
        return {
            'compute': self.supported_resources[provider],
            'networking': ['vpc', 'subnet', 'security_group'],
            'storage': ['s3', 'ebs'] if provider == 'aws' else ['storage_account', 'disk'],
            'database': ['rds'] if provider == 'aws' else ['sql_database']
        }

# Instancia global del generador
iac_generator = IaCGenerator()