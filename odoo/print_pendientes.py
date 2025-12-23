#!/usr/bin/env python3
"""
Print Pendientes - JSON Output
==============================

Wrapper que reutiliza odoo/pendientes.py para imprimir JSON.

Uso:
    python -m odoo.print_pendientes --only FactorIT --pretty
    python -m odoo.print_pendientes --only FactorIT2 --pretty
    python -m odoo.print_pendientes --only FactorIT --out /tmp/factorit.json
"""

import sys
import json
import argparse
from datetime import datetime

# Reutilizar el módulo existente
from odoo.pendientes import obtener_pendientes_empresa, JSONEncoder


def main():
    parser = argparse.ArgumentParser(description='Print pendientes en JSON')
    parser.add_argument(
        '--only',
        required=True,
        choices=['FactorIT', 'FactorIT2'],
        help='Base de datos a consultar (obligatorio)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Formato con indent=2'
    )
    parser.add_argument(
        '--out',
        type=str,
        help='Archivo de salida (opcional, default: stdout)'
    )
    
    args = parser.parse_args()
    
    # Obtener pendientes usando la función existente
    pendientes = obtener_pendientes_empresa(args.only)
    
    # Estructura de salida solicitada
    output = {
        "generated_at": datetime.now().isoformat(),
        "db_alias": args.only,
        "pendientes": pendientes
    }
    
    # Serializar
    indent = 2 if args.pretty else None
    json_str = json.dumps(output, cls=JSONEncoder, ensure_ascii=False, indent=indent)
    
    # Output
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"✅ Guardado en: {args.out}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == '__main__':
    main()
