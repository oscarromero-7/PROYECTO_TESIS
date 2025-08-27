output "vm_public_ip" {
  description = "La IP pública de la máquina virtual."
  value       = azurerm_public_ip.pip.ip_address
}

output "vm_private_ip" {
  description = "La IP privada de la máquina virtual."
  value       = azurerm_network_interface.nic.private_ip_address
}
