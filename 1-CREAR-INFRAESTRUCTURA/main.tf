# Aquí iría la configuración del proveedor y del grupo de recursos si no los defines en el módulo.
# Por simplicidad, asumimos que el módulo se encarga de todo.
module "vm" {
  source = "./modulos/vm"
  vm_password = var.vm_password
  # Puedes añadir más variables aquí si las necesitas (ej. nombre del grupo de recursos, ubicación)
}
