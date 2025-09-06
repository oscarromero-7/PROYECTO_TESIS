output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = module.aws_ec2.instance_public_ip
}

output "instance_private_ip" {
  description = "Private IP address of the EC2 instance" 
  value       = module.aws_ec2.instance_private_ip
}

# Mantén los otros outputs como están
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = module.aws_ec2.instance_id
}

output "security_group_id" {
  description = "ID of the security group"
  value       = module.aws_ec2.security_group_id
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.aws_ec2.vpc_id
}

output "subnet_id" {
  description = "ID of the public subnet"
  value       = module.aws_ec2.subnet_id
}

output "key_name" {
  description = "Name of the key pair"
  value       = module.aws_ec2.key_name
}

output "private_key_path" {
  description = "Path to the private key file"
  value       = module.aws_ec2.private_key_path
}