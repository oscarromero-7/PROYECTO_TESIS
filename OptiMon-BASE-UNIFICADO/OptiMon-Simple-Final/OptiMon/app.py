
import flask
import subprocess
import webbrowser
import time
import threading

app = flask.Flask(__name__)

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OptiMon - Sistema de Monitoreo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .hero {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            margin: 40px auto;
            max-width: 1200px;
            padding: 60px 40px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .logo {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        
        h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.3rem;
            color: #666;
            margin-bottom: 50px;
            font-weight: 400;
        }
        
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 50px 0;
        }
        
        .service-card {
            background: white;
            border-radius: 20px;
            padding: 40px 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .service-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        
        .service-icon {
            font-size: 3rem;
            margin-bottom: 20px;
            display: block;
        }
        
        .service-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
        
        .service-desc {
            color: #666;
            margin-bottom: 25px;
            line-height: 1.6;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 500;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #4CAF50;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .next-steps {
            background: rgba(255,255,255,0.7);
            border-radius: 20px;
            padding: 40px;
            margin-top: 40px;
            text-align: left;
        }
        
        .step {
            margin: 20px 0;
            padding: 15px 0;
            border-bottom: 1px solid rgba(0,0,0,0.1);
        }
        
        .step:last-child {
            border-bottom: none;
        }
        
        .step-number {
            display: inline-block;
            width: 30px;
            height: 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            margin-right: 15px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="hero">
        <div class="logo">🚀</div>
        <h1>OptiMon</h1>
        <p class="subtitle">Sistema de Monitoreo Profesional</p>
        
        <div style="background: linear-gradient(45deg, #4CAF50, #45a049); color: white; padding: 20px; border-radius: 15px; margin: 30px 0;">
            <h2 style="margin: 0;">✅ Instalación Completada Exitosamente</h2>
            <p style="margin: 10px 0 0 0;">Tu sistema de monitoreo está funcionando correctamente</p>
        </div>
        
        <div class="services-grid">
            <div class="service-card">
                <span class="service-icon">📊</span>
                <h3 class="service-title">
                    <span class="status-indicator"></span>
                    Portal OptiMon
                </h3>
                <p class="service-desc">Panel de control principal del sistema</p>
                <a href="http://localhost:5000" class="btn">Acceder</a>
            </div>
            
            <div class="service-card">
                <span class="service-icon">📈</span>
                <h3 class="service-title">
                    <span class="status-indicator"></span>
                    Grafana
                </h3>
                <p class="service-desc">Dashboards visuales y métricas en tiempo real</p>
                <a href="http://localhost:3000" target="_blank" class="btn">Abrir Grafana</a>
                <div style="font-size: 0.85rem; color: #888; margin-top: 10px;">
                    Usuario: admin | Contraseña: admin
                </div>
            </div>
            
            <div class="service-card">
                <span class="service-icon">🔍</span>
                <h3 class="service-title">
                    <span class="status-indicator"></span>
                    Prometheus
                </h3>
                <p class="service-desc">Motor de métricas y consultas PromQL</p>
                <a href="http://localhost:9090" target="_blank" class="btn">Explorar Métricas</a>
            </div>
        </div>
        
        <div class="next-steps">
            <h3 style="color: #333; margin-bottom: 30px;">🎯 Próximos Pasos</h3>
            
            <div class="step">
                <span class="step-number">1</span>
                <strong>Explora Grafana:</strong> Accede a los dashboards preconfigurados para ver métricas de tu sistema en tiempo real
            </div>
            
            <div class="step">
                <span class="step-number">2</span>
                <strong>Configura Alertas:</strong> Personaliza los umbrales de alertas según tus necesidades
            </div>
            
            <div class="step">
                <span class="step-number">3</span>
                <strong>Integra Azure:</strong> Conecta tus recursos de Azure para monitoreo en la nube
            </div>
            
            <div class="step">
                <span class="step-number">4</span>
                <strong>Disfruta OptiMon:</strong> ¡Tu sistema de monitoreo está listo para usar!
            </div>
        </div>
    </div>
</body>
</html>
    """

@app.route('/api/health')
def health():
    return {"status": "ok", "service": "OptiMon", "version": "3.0.0"}

if __name__ == "__main__":
    print("🚀 Iniciando OptiMon Portal...")
    print("📊 Portal: http://localhost:5000")
    print("📈 Grafana: http://localhost:3000 (admin/admin)")
    print("🔍 Prometheus: http://localhost:9090")
    app.run(host="0.0.0.0", port=5000, debug=False)
