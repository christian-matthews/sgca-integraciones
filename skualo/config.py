"""
Gestión de configuración de empresas.
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict

# Directorio de configuraciones (dentro de skualo/)
CONFIG_DIR = Path(__file__).parent / 'config' / 'empresas'
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def get_config_path(rut: str) -> Path:
    """Obtiene la ruta del archivo de configuración de una empresa."""
    return CONFIG_DIR / f'{rut}.json'


def config_existe(rut: str) -> bool:
    """Verifica si existe configuración para una empresa."""
    return get_config_path(rut).exists()


def cargar_config(rut: str) -> Optional[Dict]:
    """
    Carga la configuración de una empresa.
    
    Args:
        rut: RUT de la empresa (ej: '77285542-7')
    
    Returns:
        dict con la configuración o None si no existe
    """
    path = get_config_path(rut)
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def guardar_config(rut: str, config: dict) -> str:
    """
    Guarda la configuración de una empresa.
    
    Args:
        rut: RUT de la empresa
        config: Diccionario con la configuración
    
    Returns:
        Ruta del archivo guardado
    """
    path = get_config_path(rut)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return str(path)


def listar_empresas() -> List[Dict]:
    """
    Lista todas las empresas configuradas.
    
    Returns:
        Lista de diccionarios con la configuración de cada empresa
    """
    empresas = []
    for config_path in CONFIG_DIR.glob('*.json'):
        with open(config_path, 'r', encoding='utf-8') as f:
            empresas.append(json.load(f))
    return empresas

