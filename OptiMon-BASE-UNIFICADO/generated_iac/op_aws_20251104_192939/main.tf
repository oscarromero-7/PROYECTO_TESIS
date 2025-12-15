# OptiMon Generated Infrastructure - AWS
# Generated on: 2025-11-04 19:29:39
# Configuration: OptiMon Infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "OptiMon"
      ManagedBy   = "OptiMon-IaC"
      CreatedOn   = "2025-11-04 19:29:39"
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "staging"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "op"
}


# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-west-2a"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "${var.project_name}-public-subnet"
    Type = "Public"
  }
}

# Private Subnet
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-west-2a"
  
  tags = {
    Name = "${var.project_name}-private-subnet"
    Type = "Private"
  }
}

# Route Table for Public Subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

# Route Table Association
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}
\n
# EC2 Instance - web-server-1
resource "aws_instance" "web_server_1" {
  ami                    = "ami-0abcdef1234567890"
  instance_type         = "t3.micro"
  key_name              = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.web_server_1_sg.id]
  subnet_id             = ""
  
  root_block_device {
    volume_type = "gp3"
    volume_size = 20
    encrypted   = true
  }
  
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              
              EOF
  
  tags = {
    Name = "${var.project_name}-web-server-1-${var.environment}"
    Type = "EC2Instance"
  }
}

# Security Group for web-server-1
resource "aws_security_group" "web_server_1_sg" {
  name_prefix = "${var.project_name}-web-server-1-"
  description = "Security group for web-server-1"
  
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow SSH (22)"
  }
  
  tags = {
    Name = "${var.project_name}-web-server-1-sg"
  }
}
\n
variable "key_pair_name" {
  description = "AWS Key Pair name"
  type        = string
}

# Outputs
output "vpc_id" { value = aws_vpc.main.id }\noutput "public_subnet_id" { value = aws_subnet.public.id }\noutput "web-server-1_public_ip" { value = aws_instance.web_server_1.public_ip }
