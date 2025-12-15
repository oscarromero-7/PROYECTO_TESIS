#!/usr/bin/env python3
"""
OptiMon Infrastructure as Code (IaC) - Demo y Pruebas
Demuestra la funcionalidad del generador de infraestructura
"""

import json
from pathlib import Path
from iac_generator import iac_generator

def demo_aws_infrastructure():
    """Demostrar generación de infraestructura AWS"""
    print("🚀 Generando infraestructura AWS de ejemplo...")
    
    config = {
        "provider": "aws",
        "project_name": "optimon-demo",
        "environment": "dev",
        "region": "us-west-2",
        "include_networking": True,
        "networking": {
            "vpc_cidr": "10.0.0.0/16",
            "public_subnet_cidr": "10.0.1.0/24",
            "private_subnet_cidr": "10.0.2.0/24",
            "availability_zone": "us-west-2a"
        },
        "compute_resources": [
            {
                "name": "web-server-1",
                "instance_type": "t3.micro",
                "volume_size": 20,
                "volume_type": "gp3",
                "security_rules": [
                    {
                        "type": "ingress",
                        "from_port": 22,
                        "to_port": 22,
                        "protocol": "tcp",
                        "cidr": "0.0.0.0/0",
                        "description": "SSH access"
                    },
                    {
                        "type": "ingress",
                        "from_port": 80,
                        "to_port": 80,
                        "protocol": "tcp",
                        "cidr": "0.0.0.0/0",
                        "description": "HTTP access"
                    },
                    {
                        "type": "ingress",
                        "from_port": 443,
                        "to_port": 443,
                        "protocol": "tcp",
                        "cidr": "0.0.0.0/0",
                        "description": "HTTPS access"
                    }
                ],
                "user_data": "yum install -y httpd\\nsystemctl start httpd\\nsystemctl enable httpd"
            },
            {
                "name": "app-server-1",
                "instance_type": "t3.small",
                "volume_size": 30,
                "volume_type": "gp3",
                "security_rules": [
                    {
                        "type": "ingress",
                        "from_port": 22,
                        "to_port": 22,
                        "protocol": "tcp",
                        "cidr": "10.0.0.0/16",
                        "description": "SSH from VPC"
                    },
                    {
                        "type": "ingress",
                        "from_port": 8080,
                        "to_port": 8080,
                        "protocol": "tcp",
                        "cidr": "10.0.1.0/24",
                        "description": "App port from public subnet"
                    }
                ]
            }
        ]
    }
    
    # Generar infraestructura
    output_path = iac_generator.save_infrastructure(config, "demo_aws_infrastructure")
    print(f"✅ Infraestructura AWS generada en: {output_path}")
    
    return output_path

def demo_azure_infrastructure():
    """Demostrar generación de infraestructura Azure"""
    print("🚀 Generando infraestructura Azure de ejemplo...")
    
    config = {
        "provider": "azure",
        "project_name": "optimon-azure-demo",
        "environment": "staging",
        "region": "East US",
        "include_networking": True,
        "networking": {
            "vnet_cidr": "10.1.0.0/16",
            "subnet_cidr": "10.1.1.0/24"
        },
        "compute_resources": [
            {
                "name": "web-vm",
                "vm_size": "Standard_B2s",
                "disk_type": "Standard_LRS",
                "image_publisher": "Canonical",
                "image_offer": "0001-com-ubuntu-server-focal",
                "image_sku": "20_04-lts-gen2",
                "security_rules": [
                    {
                        "name": "AllowSSH",
                        "direction": "Inbound",
                        "access": "Allow",
                        "protocol": "Tcp",
                        "port_range": "22",
                        "source": "*"
                    },
                    {
                        "name": "AllowHTTP",
                        "direction": "Inbound",
                        "access": "Allow",
                        "protocol": "Tcp",
                        "port_range": "80",
                        "source": "*"
                    },
                    {
                        "name": "AllowHTTPS",
                        "direction": "Inbound",
                        "access": "Allow",
                        "protocol": "Tcp",
                        "port_range": "443",
                        "source": "*"
                    }
                ]
            }
        ]
    }
    
    # Generar infraestructura
    output_path = iac_generator.save_infrastructure(config, "demo_azure_infrastructure")
    print(f"✅ Infraestructura Azure generada en: {output_path}")
    
    return output_path

def show_generated_files(output_path):
    """Mostrar archivos generados"""
    print(f"\n📁 Archivos generados en {output_path}:")
    print("-" * 50)
    
    path_obj = Path(output_path)
    for file_path in sorted(path_obj.glob("*")):
        if file_path.is_file():
            size = file_path.stat().st_size
            print(f"  📄 {file_path.name} ({size} bytes)")
    
    print("\n📋 Contenido del archivo main.tf:")
    print("-" * 50)
    
    main_tf = path_obj / "main.tf"
    if main_tf.exists():
        with open(main_tf, 'r', encoding='utf-8') as f:
            content = f.read()
            # Mostrar solo las primeras líneas
            lines = content.split('\n')[:30]
            for i, line in enumerate(lines, 1):
                print(f"{i:3d}: {line}")
            if len(content.split('\n')) > 30:
                print("    ... (contenido truncado)")
    
    print(f"\n💡 Para desplegar:")
    print(f"   cd {output_path}")
    print("   terraform init")
    print("   terraform plan")
    print("   terraform apply")

def demo_cost_estimation():
    """Demostrar estimación de costos"""
    print("\n💰 Estimación de costos:")
    print("-" * 30)
    
    # Ejemplo AWS
    aws_config = {
        "provider": "aws",
        "compute_resources": [
            {"instance_type": "t3.micro", "name": "web-1"},
            {"instance_type": "t3.small", "name": "app-1"}
        ]
    }
    
    # Estimación manual (en producción sería más precisa)
    costs = {
        "t3.micro": {"hourly": 0.0104, "monthly": 7.5},
        "t3.small": {"hourly": 0.0208, "monthly": 15.0}
    }
    
    total_monthly = 0
    for resource in aws_config["compute_resources"]:
        instance_type = resource["instance_type"]
        cost = costs.get(instance_type, {"monthly": 0})
        total_monthly += cost["monthly"]
        print(f"  {resource['name']} ({instance_type}): ${cost['monthly']:.2f}/mes")
    
    print(f"  TOTAL: ${total_monthly:.2f}/mes (${total_monthly * 12:.2f}/año)")
    
    print("\n⚠️  Nota: Estos son costos estimados. Los precios reales pueden variar.")

def main():
    """Función principal del demo"""
    print("=" * 60)
    print("🏗️  OptiMon Infrastructure as Code - Demo")
    print("=" * 60)
    
    try:
        # Demo AWS
        aws_path = demo_aws_infrastructure()
        show_generated_files(aws_path)
        
        print("\n" + "=" * 60)
        
        # Demo Azure
        azure_path = demo_azure_infrastructure()
        show_generated_files(azure_path)
        
        # Demo de costos
        demo_cost_estimation()
        
        print("\n✅ Demo completado exitosamente!")
        print(f"\n📂 Archivos generados disponibles en:")
        print(f"   - AWS: {aws_path}")
        print(f"   - Azure: {azure_path}")
        
        print(f"\n🌐 Interfaz web disponible en:")
        print(f"   http://localhost:5000/infrastructure")
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()