#!/usr/bin/env python3
"""
Script mejorado para gestionar visibilidad de dashboards usando carpetas
"""

import requests
import json

def manage_dashboards_visibility(hide=True):
    """Gestionar visibilidad moviendo dashboards a carpetas"""
    grafana_url = "http://localhost:3000"
    auth = ('admin', 'admin')
    
    try:
        # Crear carpeta oculta si no existe
        folder_data = {
            "title": "[HIDDEN] Cloud Dashboards",
            "uid": "hidden-cloud-dashboards"
        }
        
        folder_response = requests.post(f"{grafana_url}/api/folders", 
                                      json=folder_data, auth=auth)
        
        if folder_response.status_code == 409:  # Ya existe
            print("📁 Carpeta HIDDEN ya existe")
        elif folder_response.status_code == 200:
            print("📁 Carpeta HIDDEN creada")
        
        # Obtener ID de la carpeta
        folders_response = requests.get(f"{grafana_url}/api/folders", auth=auth)
        hidden_folder_id = None
        if folders_response.status_code == 200:
            folders = folders_response.json()
            for folder in folders:
                if folder.get('uid') == 'hidden-cloud-dashboards':
                    hidden_folder_id = folder.get('id')
                    break
        
        # Obtener lista de dashboards
        response = requests.get(f"{grafana_url}/api/search", auth=auth)
        if response.status_code != 200:
            print(f"Error obteniendo dashboards: {response.status_code}")
            return
        
        dashboards = response.json()
        processed_count = 0
        
        for dashboard in dashboards:
            uid = dashboard.get('uid')
            title = dashboard.get('title', '')
            folder_id = dashboard.get('folderId', 0)
            
            # Identificar dashboards de nube
            is_cloud_dashboard = False
            if ('aws' in title.lower() or 'ec2' in title.lower()) and 'optimon' in title.lower():
                is_cloud_dashboard = True
            elif ('azure' in title.lower() or 'vm' in title.lower()) and 'optimon' in title.lower():
                is_cloud_dashboard = True
            
            if is_cloud_dashboard:
                # Obtener dashboard completo
                dash_response = requests.get(f"{grafana_url}/api/dashboards/uid/{uid}", auth=auth)
                if dash_response.status_code == 200:
                    dash_data = dash_response.json()
                    dashboard_config = dash_data.get('dashboard', {})
                    
                    if hide:
                        # Mover a carpeta oculta
                        if folder_id != hidden_folder_id:
                            dashboard_config['folderId'] = hidden_folder_id
                            # Limpiar título si tiene [HIDDEN]
                            if title.startswith('[HIDDEN]'):
                                dashboard_config['title'] = title.replace('[HIDDEN] ', '')
                            
                            update_data = {
                                'dashboard': dashboard_config,
                                'folderId': hidden_folder_id,
                                'message': 'Moved to hidden folder due to missing credentials',
                                'overwrite': True
                            }
                            
                            update_response = requests.post(f"{grafana_url}/api/dashboards/db", 
                                                          json=update_data, auth=auth)
                            if update_response.status_code == 200:
                                print(f"📁 Dashboard movido a carpeta oculta: {title}")
                                processed_count += 1
                            else:
                                print(f"❌ Error moviendo dashboard: {title} - {update_response.status_code}")
                    else:
                        # Mover de vuelta a root
                        if folder_id == hidden_folder_id:
                            dashboard_config['folderId'] = 0  # Root folder
                            
                            update_data = {
                                'dashboard': dashboard_config,
                                'folderId': 0,
                                'message': 'Restored to root folder',
                                'overwrite': True
                            }
                            
                            update_response = requests.post(f"{grafana_url}/api/dashboards/db", 
                                                          json=update_data, auth=auth)
                            if update_response.status_code == 200:
                                print(f"📁 Dashboard restaurado: {title}")
                                processed_count += 1
                            else:
                                print(f"❌ Error restaurando dashboard: {title} - {update_response.status_code}")
        
        action = "ocultados" if hide else "restaurados"
        print(f"\n🎯 Total de dashboards {action}: {processed_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def delete_cloud_dashboards():
    """Eliminar temporalmente dashboards de nube"""
    grafana_url = "http://localhost:3000"
    auth = ('admin', 'admin')
    
    try:
        # Obtener lista de dashboards
        response = requests.get(f"{grafana_url}/api/search", auth=auth)
        if response.status_code != 200:
            print(f"Error obteniendo dashboards: {response.status_code}")
            return
        
        dashboards = response.json()
        deleted_count = 0
        
        for dashboard in dashboards:
            uid = dashboard.get('uid')
            title = dashboard.get('title', '')
            
            # Identificar dashboards de nube
            is_cloud_dashboard = False
            if ('aws' in title.lower() or 'ec2' in title.lower()) and 'optimon' in title.lower():
                is_cloud_dashboard = True
            elif ('azure' in title.lower() or 'vm' in title.lower()) and 'optimon' in title.lower():
                is_cloud_dashboard = True
            
            if is_cloud_dashboard:
                # Eliminar dashboard
                delete_response = requests.delete(f"{grafana_url}/api/dashboards/uid/{uid}", auth=auth)
                if delete_response.status_code == 200:
                    print(f"🗑️ Dashboard eliminado: {title}")
                    deleted_count += 1
                else:
                    print(f"❌ Error eliminando dashboard: {title} - {delete_response.status_code}")
        
        print(f"\n🎯 Total de dashboards eliminados: {deleted_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'show':
            manage_dashboards_visibility(hide=False)
        elif sys.argv[1] == 'delete':
            delete_cloud_dashboards()
        else:
            manage_dashboards_visibility(hide=True)
    else:
        manage_dashboards_visibility(hide=True)