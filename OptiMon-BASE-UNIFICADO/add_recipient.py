#!/usr/bin/env python3
import requests
import json

# Configurar destinatario
response = requests.post(
    'http://localhost:5000/api/email/config',
    headers={'Content-Type': 'application/json'},
    json={'recipients': ['wacry77@gmail.com']}
)

print("Configurando destinatario...")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Resultado: {result}")
else:
    print(f"Error: {response.text}")