#!/usr/bin/env python3
"""
OptiMon - Script de Pruebas del Sistema
Verifica que todos los componentes estén funcionando correctamente
"""

import requests
import time
import sys
import subprocess
from pathlib import Path

class SystemTester:
    def __init__(self):
        self.services = {
            'prometheus': {'port': 9090, 'path': '/-/healthy'},
            'grafana': {'port': 3000, 'path': '/api/health'},
            'alertmanager': {'port': 9093, 'path': '/-/healthy'}
        }
        
    def test_docker_services(self):
        """Verifica que los servicios Docker estén ejecutándose"""
        print("🐳 Verificando servicios Docker...")
        
        try:
            result = subprocess.run(['docker-compose', 'ps'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                running_services = []
                
                for line in output.split('\n'):
                    if 'Up' in line:
                        service_name = line.split()[0]
                        running_services.append(service_name)
                
                print(f"  ✅ Servicios ejecutándose: {', '.join(running_services)}")
                return True
            else:
                print("  ❌ Error consultando servicios Docker")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def test_service_health(self, service_name, port, path):
        """Verifica que un servicio específico esté respondiendo"""
        url = f"http://localhost:{port}{path}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {service_name.capitalize()} respondiendo correctamente")
                return True
            else:
                print(f"  ❌ {service_name.capitalize()} respondió con código {response.status_code}")
                return False
                
        except requests.exceptions.ConnectException:
            print(f"  ❌ {service_name.capitalize()} no está accesible")
            return False
        except requests.exceptions.Timeout:
            print(f"  ❌ {service_name.capitalize()} timeout")
            return False
        except Exception as e:
            print(f"  ❌ Error conectando a {service_name}: {e}")
            return False
    
    def test_prometheus_targets(self):
        """Verifica los targets configurados en Prometheus"""
        print("🎯 Verificando targets de Prometheus...")
        
        try:
            response = requests.get('http://localhost:9090/api/v1/targets', timeout=10)
            if response.status_code == 200:
                data = response.json()
                targets = data.get('data', {}).get('activeTargets', [])
                
                up_targets = []
                down_targets = []
                
                for target in targets:
                    instance = target.get('labels', {}).get('instance', 'unknown')
                    health = target.get('health', 'unknown')
                    
                    if health == 'up':
                        up_targets.append(instance)
                    else:
                        down_targets.append(instance)
                
                print(f"  ✅ Targets activos: {len(up_targets)}")
                for target in up_targets:
                    print(f"    • {target}")
                
                if down_targets:
                    print(f"  ⚠️  Targets inactivos: {len(down_targets)}")
                    for target in down_targets:
                        print(f"    • {target}")
                
                return len(up_targets) > 0
                
            else:
                print("  ❌ Error consultando targets de Prometheus")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def test_grafana_datasource(self):
        """Verifica que Grafana tenga el datasource configurado"""
        print("📊 Verificando datasource de Grafana...")
        
        try:
            # Login en Grafana
            login_response = requests.post(
                'http://localhost:3000/login',
                json={'user': 'admin', 'password': 'admin'},
                timeout=10
            )
            
            if login_response.status_code != 200:
                print("  ❌ Error de autenticación en Grafana")
                return False
            
            # Verificar datasources
            datasources_response = requests.get(
                'http://localhost:3000/api/datasources',
                auth=('admin', 'admin'),
                timeout=10
            )
            
            if datasources_response.status_code == 200:
                datasources = datasources_response.json()
                prometheus_ds = [ds for ds in datasources if ds['type'] == 'prometheus']
                
                if prometheus_ds:
                    print("  ✅ Datasource Prometheus configurado")
                    return True
                else:
                    print("  ❌ Datasource Prometheus no encontrado")
                    return False
            else:
                print("  ❌ Error consultando datasources")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def test_alerting_rules(self):
        """Verifica que las reglas de alertas estén cargadas"""
        print("🚨 Verificando reglas de alertas...")
        
        try:
            response = requests.get('http://localhost:9090/api/v1/rules', timeout=10)
            if response.status_code == 200:
                data = response.json()
                groups = data.get('data', {}).get('groups', [])
                
                total_rules = 0
                for group in groups:
                    rules = group.get('rules', [])
                    total_rules += len(rules)
                
                print(f"  ✅ {total_rules} reglas de alertas cargadas")
                return total_rules > 0
                
            else:
                print("  ❌ Error consultando reglas de alertas")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def test_node_exporter_metrics(self):
        """Verifica que se puedan obtener métricas básicas"""
        print("📈 Verificando métricas de Node Exporter...")
        
        try:
            # Consultar métrica básica
            query = 'up{job="node-exporter"}'
            response = requests.get(
                'http://localhost:9090/api/v1/query',
                params={'query': query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('data', {}).get('result', [])
                
                if results:
                    instances = [r['metric'].get('instance', 'unknown') for r in results]
                    print(f"  ✅ Métricas disponibles para: {', '.join(instances)}")
                    return True
                else:
                    print("  ⚠️  No se encontraron métricas de Node Exporter")
                    return False
            else:
                print("  ❌ Error consultando métricas")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def test_configuration_files(self):
        """Verifica que los archivos de configuración existan"""
        print("📁 Verificando archivos de configuración...")
        
        required_files = [
            'config/prometheus/prometheus.yml',
            'config/prometheus/alert.rules.yml',
            'config/grafana/provisioning/datasources/prometheus.yml',
            'config/alertmanager/alertmanager.yml'
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            if Path(file_path).exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        print(f"  ✅ Archivos existentes: {len(existing_files)}")
        for file_path in existing_files:
            print(f"    • {file_path}")
        
        if missing_files:
            print(f"  ❌ Archivos faltantes: {len(missing_files)}")
            for file_path in missing_files:
                print(f"    • {file_path}")
            return False
        
        return True
    
    def run_full_test(self):
        """Ejecuta todas las pruebas"""
        print("🧪 OptiMon - Pruebas del Sistema")
        print("=" * 40)
        
        tests = [
            ("Configuración", self.test_configuration_files),
            ("Servicios Docker", self.test_docker_services),
            ("Prometheus", lambda: self.test_service_health('prometheus', 9090, '/-/healthy')),
            ("Grafana", lambda: self.test_service_health('grafana', 3000, '/api/health')),
            ("AlertManager", lambda: self.test_service_health('alertmanager', 9093, '/-/healthy')),
            ("Targets Prometheus", self.test_prometheus_targets),
            ("Datasource Grafana", self.test_grafana_datasource),
            ("Reglas de Alertas", self.test_alerting_rules),
            ("Métricas Node Exporter", self.test_node_exporter_metrics)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n🔍 Probando {test_name}...")
            try:
                result = test_func()
                results.append((test_name, result))
                
                if result:
                    print(f"✅ {test_name}: PASS")
                else:
                    print(f"❌ {test_name}: FAIL")
                    
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                results.append((test_name, False))
        
        # Resumen final
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"✅ Pruebas exitosas: {passed}/{total}")
        print(f"❌ Pruebas fallidas: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 ¡Todos los tests pasaron! El sistema está funcionando correctamente.")
            print("\n📋 Próximos pasos:")
            print("  • Accede a Grafana: http://localhost:3000 (admin/admin)")
            print("  • Revisa Prometheus: http://localhost:9090")
            print("  • Configura alertas: http://localhost:9093")
        else:
            print(f"\n⚠️  {total - passed} pruebas fallaron. Revisa la configuración.")
            print("\n🔧 Comandos útiles para debugging:")
            print("  • Ver logs: docker-compose logs -f")
            print("  • Reiniciar servicios: docker-compose restart")
            print("  • Verificar configuración: python scripts/setup_prometheus.py")
        
        return passed == total

if __name__ == "__main__":
    try:
        tester = SystemTester()
        
        if len(sys.argv) > 1:
            if sys.argv[1] == "quick":
                # Prueba rápida solo de servicios básicos
                print("🚀 Prueba rápida de servicios...")
                tester.test_docker_services()
                for service, config in tester.services.items():
                    tester.test_service_health(service, config['port'], config['path'])
            elif sys.argv[1] == "targets":
                # Solo prueba targets
                tester.test_prometheus_targets()
            elif sys.argv[1] == "config":
                # Solo prueba configuración
                tester.test_configuration_files()
        else:
            # Prueba completa
            success = tester.run_full_test()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n❌ Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        sys.exit(1)