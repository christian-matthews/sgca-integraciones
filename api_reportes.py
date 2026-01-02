#!/usr/bin/env python3
"""
API de Reportes SGCA
====================

Endpoint Flask para generación on-demand de reportes Excel.

Uso:
    python api_reportes.py                    # Puerto 5001
    FLASK_PORT=8080 python api_reportes.py    # Puerto custom

Endpoints:
    GET  /health                              → Health check
    GET  /api/reports/pendientes/{empresa}    → Reporte pendientes
    POST /api/reports/financiero              → Reporte financiero con fecha corte
"""

import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

app = Flask(__name__)
CORS(app)  # Permitir requests desde frontend

# Mapeo de company_id/alias a ERP y configuración
COMPANY_ERP_MAP = {
    # Skualo (The Wingman)
    "FIDI": {"erp": "skualo", "id": "FIDI"},
    "CISI": {"erp": "skualo", "id": "CISI"},
    "fidi": {"erp": "skualo", "id": "FIDI"},
    "cisitel": {"erp": "skualo", "id": "CISI"},
    
    # Odoo (FactorIT)
    "FactorIT": {"erp": "odoo", "id": "FactorIT"},
    "FactorIT2": {"erp": "odoo", "id": "FactorIT2"},
    "factorit_spa": {"erp": "odoo", "id": "FactorIT"},
    "factorit_ltda": {"erp": "odoo", "id": "FactorIT2"},
}

# ═══════════════════════════════════════════════════════════════════════════════
# IMPORTS DINÁMICOS
# ═══════════════════════════════════════════════════════════════════════════════

def get_skualo_pendientes():
    from skualo.reports.pendientes_excel import generar_reporte
    return generar_reporte

def get_odoo_pendientes():
    from odoo.reports.pendientes_excel import generar_reporte
    return generar_reporte

def get_skualo_balance():
    from skualo.reports.balance_excel import generar_reporte
    return generar_reporte

def get_odoo_balance():
    from odoo.reports.balance_excel import generar_reporte
    return generar_reporte


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health():
    """Health check."""
    return jsonify({
        "status": "ok",
        "service": "sgca-reportes",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/reports/pendientes/<empresa>', methods=['GET'])
def reporte_pendientes(empresa: str):
    """
    Genera reporte de pendientes on-demand.
    
    Args:
        empresa: Alias de empresa (FIDI, CISI, FactorIT, FactorIT2)
    
    Returns:
        Excel file download
    """
    try:
        config = COMPANY_ERP_MAP.get(empresa)
        if not config:
            return jsonify({"error": f"Empresa no encontrada: {empresa}"}), 404
        
        erp = config["erp"]
        empresa_id = config["id"]
        
        print(f"📊 Generando pendientes para {empresa_id} (ERP: {erp})...")
        
        if erp == "skualo":
            generar = get_skualo_pendientes()
        else:
            generar = get_odoo_pendientes()
        
        filepath = generar(empresa_id)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"Pendientes_{empresa_id}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# REPORTE FINANCIERO - DESHABILITADO TEMPORALMENTE
# ═══════════════════════════════════════════════════════════════════════════════
# Motivo: Contiene información sensible de clientes
# Para habilitar: cambiar FINANCIERO_HABILITADO = True
# ═══════════════════════════════════════════════════════════════════════════════
FINANCIERO_HABILITADO = True


@app.route('/api/reports/financiero', methods=['POST'])
def reporte_financiero():
    """
    Genera reporte financiero (balance + análisis) on-demand.
    
    Body JSON:
        {
            "empresa": "FIDI",
            "fecha_corte": "2025-12-31"
        }
    
    Returns:
        Excel file download
    """
    # Check si está habilitado
    if not FINANCIERO_HABILITADO:
        return jsonify({
            "error": "Reporte financiero temporalmente deshabilitado",
            "message": "Este reporte contiene información sensible. Contacte al administrador."
        }), 403
    
    try:
        data = request.get_json()
        empresa = data.get("empresa")
        fecha_corte = data.get("fecha_corte")
        
        if not empresa:
            return jsonify({"error": "Campo 'empresa' requerido"}), 400
        if not fecha_corte:
            return jsonify({"error": "Campo 'fecha_corte' requerido"}), 400
        
        config = COMPANY_ERP_MAP.get(empresa)
        if not config:
            return jsonify({"error": f"Empresa no encontrada: {empresa}"}), 404
        
        erp = config["erp"]
        empresa_id = config["id"]
        
        print(f"📊 Generando financiero para {empresa_id} al {fecha_corte} (ERP: {erp})...")
        
        if erp == "skualo":
            generar = get_skualo_balance()
            filepath = generar(empresa_id, fecha_corte)
        else:
            generar = get_odoo_balance()
            filepath = generar(empresa_id, fecha_corte)
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"Financiero_{empresa_id}_{fecha_corte}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/reports/available/<empresa>', methods=['GET'])
def reportes_disponibles(empresa: str):
    """
    Lista reportes disponibles para una empresa.
    """
    config = COMPANY_ERP_MAP.get(empresa)
    if not config:
        return jsonify({"error": f"Empresa no encontrada: {empresa}"}), 404
    
    erp = config["erp"]
    
    reportes = [
        {
            "id": "pendientes",
            "nombre": "Reporte de Pendientes",
            "descripcion": "SII, Contabilizar, Conciliar",
            "requiere_fecha": False,
            "disponible": True
        },
        {
            "id": "financiero",
            "nombre": "Reporte Financiero",
            "descripcion": "Balance, EERR, Análisis por cuenta",
            "requiere_fecha": True,
            "disponible": FINANCIERO_HABILITADO  # Deshabilitado temporalmente
        }
    ]
    
    return jsonify({
        "empresa": empresa,
        "erp": erp,
        "reportes": reportes
    })


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5001))
    print(f"""
═══════════════════════════════════════════════════════════════
   SGCA API de Reportes
   Puerto: {port}
═══════════════════════════════════════════════════════════════

Endpoints:
  GET  /health
  GET  /api/reports/pendientes/<empresa>
  POST /api/reports/financiero
  GET  /api/reports/available/<empresa>

Empresas disponibles:
  Skualo: FIDI, CISI
  Odoo:   FactorIT, FactorIT2

═══════════════════════════════════════════════════════════════
""")
    app.run(host='0.0.0.0', port=port, debug=True)
