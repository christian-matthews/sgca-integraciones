"""
Odoo Integration Module
=======================

Módulo para integración con bases de datos Odoo (PostgreSQL).

Empresas configuradas:
- FactorIT SpA (DB: FactorIT)
- FactorIT Ltda (DB: FactorIT2)

Configuración (.env):
    SERVER=18.223.205.221
    PORT=5432
    DB_USER=Hector
    PASSWORD=tu_password

Uso:
    # Test de conexión
    python -m odoo.test_connection
    
    # Reporte de pendientes (JSON)
    python -m odoo.pendientes
    
    # Balance + Estado de Resultados (Excel)
    python -m odoo.balance_excel FactorIT
    
    # Como módulo
    from odoo import obtener_pendientes
    data = obtener_pendientes()  # Retorna dict con todos los pendientes
"""

__version__ = '1.1.0'


# Lazy imports para evitar errores si psycopg2 no está instalado
def test_connection(db_name, db_info):
    """Test de conexión a una base de datos específica."""
    from .test_connection import test_connection as _test
    return _test(db_name, db_info)


def obtener_pendientes():
    """Obtiene todos los pendientes de todas las empresas (JSON)."""
    from .pendientes import obtener_pendientes as _pendientes
    return _pendientes()


def obtener_pendientes_empresa(db_name: str):
    """Obtiene pendientes de una empresa específica."""
    from .pendientes import obtener_pendientes_empresa as _pendientes_emp
    return _pendientes_emp(db_name)


def generar_balance_excel(db_name: str, fecha_hasta: str = None):
    """Genera Balance + Estado de Resultados en Excel."""
    from .balance_excel import generar_balance_excel as _balance
    return _balance(db_name, fecha_hasta)


def get_databases():
    from .test_connection import DATABASES
    return DATABASES


# Para importación directa
try:
    from .test_connection import DATABASES, QUERY_PENDIENTES_SII
except ImportError:
    DATABASES = {}
    QUERY_PENDIENTES_SII = ""

__all__ = [
    'test_connection',
    'obtener_pendientes',
    'obtener_pendientes_empresa', 
    'generar_balance_excel',
    'get_databases',
    'DATABASES',
    'QUERY_PENDIENTES_SII',
]

