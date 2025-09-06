module "aws_ec2" {
  source = "./modulos/aws"
  
  aws_region    = var.aws_region
  key_name      = var.key_name
  instance_type = var.instance_type
}