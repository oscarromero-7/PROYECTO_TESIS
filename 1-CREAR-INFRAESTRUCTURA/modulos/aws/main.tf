# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# VPC
resource "aws_vpc" "optimon_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "optimon-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "optimon_igw" {
  vpc_id = aws_vpc.optimon_vpc.id

  tags = {
    Name = "optimon-igw"
  }
}

# Public Subnet
resource "aws_subnet" "optimon_public" {
  vpc_id                  = aws_vpc.optimon_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "optimon-public-subnet"
  }
}

# Route Table
resource "aws_route_table" "optimon_public" {
  vpc_id = aws_vpc.optimon_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.optimon_igw.id
  }

  tags = {
    Name = "optimon-public-rt"
  }
}

# Route Table Association
resource "aws_route_table_association" "optimon_public" {
  subnet_id      = aws_subnet.optimon_public.id
  route_table_id = aws_route_table.optimon_public.id
}

# Security Group
resource "aws_security_group" "optimon_sg" {
  name        = "optimon-sg"
  description = "Security group for OptiMon monitoring"
  vpc_id      = aws_vpc.optimon_vpc.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Node Exporter"
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Custom metrics"
    from_port   = 8080
    to_port     = 8090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "optimon-sg"
  }
}

# Key Pair
resource "aws_key_pair" "optimon_key" {
  key_name   = var.key_name
  public_key = tls_private_key.optimon_key.public_key_openssh

  tags = {
    Name = "optimon-key"
  }
}

# Generate private key
resource "tls_private_key" "optimon_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

# Save private key locally
resource "local_file" "private_key" {
  content  = tls_private_key.optimon_key.private_key_pem
  filename = "${var.key_name}.pem"
  file_permission = "0400"
}

# EC2 Instance
resource "aws_instance" "optimon_instance" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name              = aws_key_pair.optimon_key.key_name
  vpc_security_group_ids = [aws_security_group.optimon_sg.id]
  subnet_id             = aws_subnet.optimon_public.id

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    region = var.aws_region
  }))

  root_block_device {
    volume_type = "gp2"
    volume_size = 8
    encrypted   = false
  }

  tags = {
    Name = "OptiMon-EC2"
    Environment = "monitoring"
  }

  provisioner "remote-exec" {
    inline = [
      "echo 'Instance is ready'"
    ]

    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ec2-user"
      private_key = tls_private_key.optimon_key.private_key_pem
    }
  }
}