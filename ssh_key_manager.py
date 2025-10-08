#!/usr/bin/env python3
"""
SSH Key Auto-Discovery and Setup
Busca automáticamente claves SSH en todo el sistema y las configura
"""

import os
import shutil
import glob
from pathlib import Path
import re

class SSHKeyManager:
    def __init__(self):
        self.ssh_dir = Path.home() / ".ssh"
        self.potential_locations = [
            Path.home() / "Downloads",
            Path.home() / "Desktop", 
            Path.home() / "Documents",
            Path("C:/"),  # Para buscar en toda la unidad C (si es necesario)
        ]
        
        # Patrones de nombres de archivos de claves SSH
        self.key_patterns = [
            "*_key.pem", "*.pem", "*_key", "*key*", 
            "id_rsa", "id_ed25519", "azure*", "aws*",
            "*private*", "*ssh*"
        ]
        
    def find_ssh_keys_system_wide(self):
        """Busca claves SSH en todo el sistema"""
        found_keys = []
        
        print("🔍 Buscando claves SSH en el sistema...")
        
        for location in self.potential_locations:
            if not location.exists():
                continue
                
            print(f"📁 Buscando en: {location}")
            
            try:
                for pattern in self.key_patterns:
                    # Buscar recursivamente pero limitado
                    if location == Path("C:/"):
                        # Solo buscar en ubicaciones comunes en C:
                        search_paths = [
                            Path("C:/Users") / os.environ.get('USERNAME', '') / "Downloads",
                            Path("C:/Users") / os.environ.get('USERNAME', '') / "Desktop",
                            Path("C:/Users") / os.environ.get('USERNAME', '') / "Documents",
                        ]
                    else:
                        search_paths = [location]
                    
                    for search_path in search_paths:
                        if search_path.exists():
                            # Buscar archivos con el patrón
                            for key_file in search_path.rglob(pattern):
                                if self._is_potential_ssh_key(key_file):
                                    found_keys.append(key_file)
                                    print(f"  ✅ Encontrada: {key_file}")
                                    
            except (PermissionError, OSError) as e:
                print(f"  ⚠️ Sin acceso a {location}: {e}")
                continue
        
        return found_keys
    
    def _is_potential_ssh_key(self, file_path):
        """Verifica si un archivo podría ser una clave SSH"""
        if not file_path.is_file():
            return False
            
        # Verificar tamaño (claves SSH típicamente 1KB-10KB)
        size = file_path.stat().st_size
        if size < 100 or size > 50000:  # 100 bytes a 50KB
            return False
        
        try:
            # Leer primeras líneas para verificar formato
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = f.read(1000)  # Primeros 1000 caracteres
                
            # Verificar marcadores de claves SSH
            ssh_markers = [
                '-----BEGIN OPENSSH PRIVATE KEY-----',
                '-----BEGIN RSA PRIVATE KEY-----',
                '-----BEGIN EC PRIVATE KEY-----',
                '-----BEGIN PRIVATE KEY-----',
                'ssh-rsa', 'ssh-ed25519'
            ]
            
            return any(marker in first_lines for marker in ssh_markers)
            
        except Exception:
            return False
    
    def setup_ssh_keys(self, vm_name=None, vm_provider=None):
        """Configura automáticamente las claves SSH"""
        print(f"🔧 Configurando claves SSH automáticamente...")
        
        # Crear directorio .ssh si no existe
        self.ssh_dir.mkdir(exist_ok=True)
        
        # Buscar claves en el sistema
        found_keys = self.find_ssh_keys_system_wide()
        
        if not found_keys:
            print("❌ No se encontraron claves SSH en el sistema")
            return []
        
        configured_keys = []
        
        for key_file in found_keys:
            # Determinar nombre de destino
            if vm_name and vm_provider:
                dest_name = f"{vm_provider}_{vm_name}_key"
            else:
                dest_name = f"auto_{key_file.stem}"
            
            # Asegurar extensión apropiada
            if key_file.suffix.lower() == '.pem':
                dest_name += '.pem'
            
            dest_path = self.ssh_dir / dest_name
            
            # Copiar si no existe o es diferente
            if not dest_path.exists() or not self._files_are_same(key_file, dest_path):
                try:
                    shutil.copy2(key_file, dest_path)
                    
                    # Configurar permisos en sistemas Unix-like
                    if os.name != 'nt':  # No Windows
                        os.chmod(dest_path, 0o600)
                    
                    configured_keys.append(dest_path)
                    print(f"  ✅ Configurada: {dest_path}")
                    
                except Exception as e:
                    print(f"  ❌ Error copiando {key_file}: {e}")
            else:
                configured_keys.append(dest_path)
                print(f"  ✅ Ya existe: {dest_path}")
        
        return configured_keys
    
    def _files_are_same(self, file1, file2):
        """Verifica si dos archivos son iguales"""
        try:
            return file1.stat().st_size == file2.stat().st_size
        except:
            return False
    
    def get_ssh_keys_for_vm(self, vm_name, vm_provider):
        """Obtiene claves SSH específicas para una VM"""
        # Primero configurar automáticamente
        self.setup_ssh_keys(vm_name, vm_provider)
        
        # Buscar claves en .ssh
        ssh_keys = []
        if self.ssh_dir.exists():
            for key_file in self.ssh_dir.iterdir():
                if (key_file.is_file() and 
                    not key_file.name.endswith(('.pub', '.known_hosts', '.config')) and
                    self._is_potential_ssh_key(key_file)):
                    ssh_keys.append(key_file)
        
        return ssh_keys

def test_ssh_key_discovery():
    """Prueba el descubrimiento automático de claves SSH"""
    manager = SSHKeyManager()
    
    print("🧪 Probando descubrimiento automático de claves SSH")
    print("=" * 60)
    
    # Buscar claves
    keys = manager.find_ssh_keys_system_wide()
    print(f"\n📊 Resultado: {len(keys)} claves encontradas")
    
    # Configurar automáticamente
    configured = manager.setup_ssh_keys("vmPruebas01", "azure")
    print(f"\n📊 Configuradas: {len(configured)} claves")
    
    # Mostrar claves disponibles
    available = manager.get_ssh_keys_for_vm("vmPruebas01", "azure")
    print(f"\n📊 Disponibles para uso: {len(available)} claves")
    
    for key in available:
        print(f"  - {key}")

if __name__ == "__main__":
    test_ssh_key_discovery()