
# Código generado automáticamente por OptiMon
# Versión: 24
# Fecha: 2025-10-05T17:09:25.074140

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


resource "aws_instance" "instance_1" {
  ami           = "ami-0c02fb55956c7d316" # Amazon Linux 2023
  instance_type = "t3.micro"
  
  
  subnet_id = "subnet-0985d820fee671d79"
  
  
  vpc_security_group_ids = [
    
    "sg-0284c3ef74fd7aab6",
    
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
    Name = "OptiMon-Instance-1"
    Environment = "monitoring"
    GeneratedBy = "OptiMon-IaC-Generator"
  }
}

resource "aws_instance" "instance_2" {
  ami           = "ami-0c02fb55956c7d316" # Amazon Linux 2023
  instance_type = "t3.micro"
  
  
  subnet_id = "subnet-00637f2bb98a8279a"
  
  
  vpc_security_group_ids = [
    
    "sg-09dc36c8dab790dc5",
    
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
    Name = "OptiMon-Instance-2"
    Environment = "monitoring"
    GeneratedBy = "OptiMon-IaC-Generator"
  }
}


# Variables
variable "aws_region" {
  description = "Región AWS"
  type        = string
  default     = "us-east-1"
}

# Outputs

output "instance_1_public_ip" {
  value = aws_instance.instance_1.public_ip
}

output "instance_1_private_ip" {
  value = aws_instance.instance_1.private_ip
}

output "instance_2_public_ip" {
  value = aws_instance.instance_2.public_ip
}

output "instance_2_private_ip" {
  value = aws_instance.instance_2.private_ip
}
