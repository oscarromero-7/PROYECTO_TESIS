#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OptiMon - Test Server para Debug
"""

from flask import Flask, jsonify
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': 'OK',
        'message': 'OptiMon Test Server Running',
        'version': '3.0.0-TEST'
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'service': 'OptiMon Test',
        'components': {
            'server': True
        }
    })

if __name__ == '__main__':
    logger.info("🚀 Iniciando OptiMon Test Server...")
    logger.info("🌐 Puerto: 5000")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f"❌ Error iniciando servidor: {e}")