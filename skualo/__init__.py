"""
Skualo Control - Módulo de Control y Reportes Contables
========================================================

Este módulo proporciona funciones para interactuar con la API de Skualo ERP.

Instalación:
    pip install -r requirements.txt

Uso básico:
    from skualo import SkualoControl
    
    # Inicializar
    ctrl = SkualoControl()
    
    # Setup de empresa (primera vez)
    ctrl.setup_empresa('77285542-7')
    
    # Controles de pendientes
    resultado = ctrl.movimientos_bancarios_pendientes('77285542-7')
    resultado = ctrl.documentos_por_aprobar_sii('77285542-7')
    resultado = ctrl.documentos_por_contabilizar('77285542-7')
    
    # Reporte completo
    resultado = ctrl.reporte_completo('77285542-7')
    
    # Generar balance Excel
    archivo = ctrl.generar_balance_excel('77285542-7', '202511')
"""

from .control import SkualoControl
from .config import cargar_config, guardar_config, config_existe, listar_empresas

__version__ = '1.0.0'
__all__ = ['SkualoControl', 'cargar_config', 'guardar_config', 'config_existe', 'listar_empresas']

