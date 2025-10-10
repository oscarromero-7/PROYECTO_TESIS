#!/usr/bin/env python3
"""
Script para ocultar/mostrar dashboards en Grafana basado en credenciales
"""

import requests
import json

def hide_cloud_dashboards():
    """Ocultar dashboards de AWS y Azure cuando no hay credenciales"""
    grafana_url = "http://localhost:3000"
    auth = ('admin', 'admin')
    
    try:
        # Obtener lista de dashboards
        response = requests.get(f"{grafana_url}/api/search", auth=auth)
        if response.status_code != 200:
            print(f"Error obteniendo dashboards: {response.status_code}")
            return
        
        dashboards = response.json()
        hidden_count = 0
        
        for dashboard in dashboards:
            uid = dashboard.get('uid')
            title = dashboard.get('title', '')
            
            # Identificar dashboards de nube
            should_hide = False
            if ('aws' in title.lower() or 'ec2' in title.lower()) and 'optimon' in title.lower():
                should_hide = True
                print(f"🔒 Procesando dashboard AWS: {title}")
            elif ('azure' in title.lower() or 'vm' in title.lower()) and 'optimon' in title.lower():
                should_hide = True
                print(f"🔒 Procesando dashboard Azure: {title}")
            
            if should_hide and not title.startswith('[HIDDEN]'):
                # Obtener dashboard completo
                dash_response = requests.get(f"{grafana_url}/api/dashboards/uid/{uid}", auth=auth)
                if dash_response.status_code == 200:
                    dash_data = dash_response.json()
                    dashboard_config = dash_data.get('dashboard', {})
                    
                    # Cambiar título
                    dashboard_config['title'] = f"[HIDDEN] {title}"
                    
                    # Actualizar
                    update_data = {
                        'dashboard': dashboard_config,
                        'message': 'Hidden due to missing credentials',
                        'overwrite': True
                    }
                    
                    update_response = requests.post(f"{grafana_url}/api/dashboards/db", 
                                                  json=update_data, auth=auth)
                    if update_response.status_code == 200:
                        print(f"✅ Dashboard ocultado: {title}")
                        hidden_count += 1
                    else:
                        print(f"❌ Error ocultando dashboard: {title} - {update_response.status_code}")
        
        print(f"\n🎯 Total de dashboards ocultados: {hidden_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def show_cloud_dashboards():
    """Mostrar dashboards previamente ocultos"""
    grafana_url = "http://localhost:3000"
    auth = ('admin', 'admin')
    
    try:
        # Obtener lista de dashboards
        response = requests.get(f"{grafana_url}/api/search", auth=auth)
        if response.status_code != 200:
            print(f"Error obteniendo dashboards: {response.status_code}")
            return
        
        dashboards = response.json()
        shown_count = 0
        
        for dashboard in dashboards:
            uid = dashboard.get('uid')
            title = dashboard.get('title', '')
            
            if title.startswith('[HIDDEN]'):
                # Obtener dashboard completo
                dash_response = requests.get(f"{grafana_url}/api/dashboards/uid/{uid}", auth=auth)
                if dash_response.status_code == 200:
                    dash_data = dash_response.json()
                    dashboard_config = dash_data.get('dashboard', {})
                    
                    # Restaurar título
                    original_title = title.replace('[HIDDEN] ', '')
                    dashboard_config['title'] = original_title
                    
                    # Actualizar
                    update_data = {
                        'dashboard': dashboard_config,
                        'message': 'Restored visibility',
                        'overwrite': True
                    }
                    
                    update_response = requests.post(f"{grafana_url}/api/dashboards/db", 
                                                  json=update_data, auth=auth)
                    if update_response.status_code == 200:
                        print(f"✅ Dashboard restaurado: {original_title}")
                        shown_count += 1
                    else:
                        print(f"❌ Error restaurando dashboard: {title} - {update_response.status_code}")
        
        print(f"\n🎯 Total de dashboards restaurados: {shown_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'show':
        show_cloud_dashboards()
    else:
        hide_cloud_dashboards()