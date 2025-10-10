# Script para agregar segunda dirección de email a AlertManager
$configFile = "c:\Users\oagr2\Documents\GitHub\PROYECTO_TESIS\2-INICIAR-MONITOREO\config\alertmanager\alertmanager.yml"

# Leer el contenido del archivo
$content = Get-Content $configFile -Raw

# Definir el patrón para encontrar las configuraciones de email
$pattern = '(email_configs:\s*\n\s*-\s*to:\s*[''"]oagr2010@outlook\.com[''"].*?(?=\n\s*-\s*name:|$))'

# Función para agregar la segunda dirección
$replacement = {
    param($match)
    $emailConfig = $match.Groups[1].Value
    
    # Buscar el final de la primera configuración de email
    if ($emailConfig -match '(\n\s*)(\n\s*-\s*name:|\Z)') {
        $indent = $matches[1]
        $ending = $matches[2]
        
        # Crear la segunda configuración de email
        $secondEmail = @"
      - to: 'wacry77@gmail.com'
        subject: '[OptiMon] Alerta General - {{ .GroupLabels.alertname }}'
        html: |
          <h2>⚠️ Alerta OptiMon</h2>
          <p><strong>Alerta:</strong> {{ .GroupLabels.alertname }}</p>
          <p><strong>Estado:</strong> {{ .Status }}</p>
          {{ range .Alerts }}
          <div style="border-left: 3px solid #ff9800; padding: 10px; margin: 10px 0;">
            <p><strong>Servidor:</strong> {{ .Labels.server_name }}</p>
            <p><strong>Instancia:</strong> {{ .Labels.instance }}</p>
            <p><strong>Severidad:</strong> {{ .Labels.severity }}</p>
            <p><strong>Descripción:</strong> {{ .Annotations.description }}</p>
          </div>
          {{ end }}
"@
        
        return $emailConfig -replace '(\n\s*)(\n\s*-\s*name:|\Z)', "$indent$secondEmail$2"
    }
    return $emailConfig
}

# Aplicar el reemplazo
$newContent = [regex]::Replace($content, $pattern, $replacement, [System.Text.RegularExpressions.RegexOptions]::Singleline)

# Guardar el archivo
$newContent | Set-Content $configFile -NoNewline

Write-Host "✅ Segunda dirección de email agregada a todos los receptores"
Write-Host "📧 Direcciones configuradas:"
Write-Host "   • oagr2010@outlook.com"
Write-Host "   • wacry77@gmail.com"