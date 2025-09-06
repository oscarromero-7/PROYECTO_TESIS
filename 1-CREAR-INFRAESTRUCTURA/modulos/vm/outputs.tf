output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = module.aws_ec2.instance_public_ip
}

output "instance_private_ip" {
  description = "Private IP address of the EC2 instance"
  value       = module.aws_ec2.instance_private_ip
}