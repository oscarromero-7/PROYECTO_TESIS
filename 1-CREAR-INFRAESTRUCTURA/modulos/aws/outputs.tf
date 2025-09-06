output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.optimon_instance.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.optimon_instance.public_ip
}

output "instance_private_ip" {
  description = "Private IP address of the EC2 instance"
  value       = aws_instance.optimon_instance.private_ip
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.optimon_sg.id
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.optimon_vpc.id
}

output "subnet_id" {
  description = "ID of the public subnet"
  value       = aws_subnet.optimon_public.id
}

output "key_name" {
  description = "Name of the key pair"
  value       = aws_key_pair.optimon_key.key_name
}

output "private_key_path" {
  description = "Path to the private key file"
  value       = local_file.private_key.filename
}