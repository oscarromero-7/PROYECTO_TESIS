variable "vm_password" {
  type      = string
  sensitive = true
}

variable "resource_group_name" {
  type    = string
  default = "optimon-rg"
}

variable "location" {
  type    = string
  default = "East US"
}

variable "vm_username" {
  type    = string
  default = "adminuser"
}
