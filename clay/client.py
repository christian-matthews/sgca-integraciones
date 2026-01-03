#!/usr/bin/env python3
"""
Cliente API Clay.cl
==================

Base URL: https://api.clay.cl
Auth: Header "Token: {API_KEY}"

Documentación: https://api.clay.cl/docs
"""

import os
from typing import Optional, Dict, List, Any
from datetime import datetime, date
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://api.clay.cl"
TOKEN = os.getenv("CLAY_API_TOKEN")


class ClayClient:
    """Cliente para la API de Clay.cl"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or TOKEN
        if not self.token:
            raise ValueError("CLAY_API_TOKEN no configurado")
        
        self.headers = {
            "Token": self.token,
            "Accept": "application/json"
        }
    
    @staticmethod
    def normalize_rut(rut: str) -> str:
        """
        Normaliza RUT al formato que espera Clay: solo números, sin DV.
        
        Ejemplos:
            77371445-2 -> 77371445
            773714452  -> 77371445
            77371445   -> 77371445
        """
        # Remover guión y todo lo que sigue
        if "-" in rut:
            rut = rut.split("-")[0]
        # Si tiene DV pegado (longitud > 8), remover último dígito
        elif len(rut) > 8:
            rut = rut[:-1]
        return rut
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """GET request a la API"""
        url = f"{API_BASE}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def _post(self, endpoint: str, data: Dict) -> Dict:
        """POST request a la API"""
        url = f"{API_BASE}{endpoint}"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    # =========================================================================
    # EMPRESAS
    # =========================================================================
    
    def listar_empresas(self, limit: int = 100, offset: int = 0) -> Dict:
        """Lista todas las empresas disponibles"""
        return self._get("/v1/empresas/", {"limit": limit, "offset": offset})
    
    def estado_avance(self, rut: str, fecha_desde: Optional[str] = None) -> Dict:
        """Obtiene el estado de procesamiento de una empresa"""
        params = {"rut": rut}
        if fecha_desde:
            params["fecha_desde"] = fecha_desde
        return self._get("/v1/empresas/estado_avance/", params)
    
    def impuestos(self, rut: str, anio: int, mes: int) -> Dict:
        """Obtiene información de impuestos (F29)"""
        return self._get("/v1/empresas/impuestos/", {
            "rut": rut, "anio": anio, "mes": mes
        })
    
    # =========================================================================
    # OBLIGACIONES / DTEs
    # =========================================================================
    
    def documentos_pendientes(self, rut_empresa: str) -> Dict:
        """DTEs por pagar (desde RCV SII)"""
        return self._get("/v1/obligaciones/documentos_pendientes/", {
            "rut_empresa": self.normalize_rut(rut_empresa)
        })
    
    def documentos_tributarios(
        self, 
        rut_empresa: str, 
        fecha_desde: Optional[str] = None,
        tipo: Optional[str] = None,  # "recibida" o "pagada"
        limit: int = 100
    ) -> Dict:
        """Lista DTEs (emitidos/recibidos)"""
        params = {"rut_empresa": rut_empresa, "limit": limit}
        if fecha_desde:
            params["fecha_desde"] = fecha_desde
        if tipo:
            params["tipo"] = tipo
        return self._get("/v1/obligaciones/documentos_tributarios/", params)
    
    def boletas_honorarios(
        self, 
        rut_receptor: str, 
        fecha_desde: Optional[str] = None,
        limit: int = 100
    ) -> Dict:
        """Lista boletas de honorarios"""
        params = {"rut_receptor": rut_receptor, "limit": limit}
        if fecha_desde:
            params["fecha_desde"] = fecha_desde
        return self._get("/v1/obligaciones/boletas_honorarios/", params)
    
    def invoices(
        self, 
        rut_empresa: str, 
        match: Optional[bool] = None,
        limit: int = 100
    ) -> Dict:
        """Lista invoices"""
        params = {"rut_empresa": rut_empresa, "limit": limit}
        if match is not None:
            params["match"] = match
        return self._get("/v1/obligaciones/invoices/", params)
    
    # =========================================================================
    # CUENTAS BANCARIAS
    # =========================================================================
    
    def saldos_bancarios(
        self, 
        rut_empresa: str, 
        numero_cuenta: Optional[str] = None,
        fecha_desde: Optional[str] = None
    ) -> Dict:
        """Obtiene saldos bancarios"""
        params = {"rut_empresa": rut_empresa}
        if numero_cuenta:
            params["numero_cuenta"] = numero_cuenta
        if fecha_desde:
            params["fecha_desde"] = fecha_desde
        return self._get("/v1/cuentas_bancarias/saldos/", params)
    
    def movimientos_bancarios(
        self, 
        rut_empresa: str, 
        numero_cuenta: Optional[str] = None,
        con_match: Optional[bool] = None,
        limit: int = 100
    ) -> Dict:
        """Lista movimientos bancarios"""
        params = {"rut_empresa": rut_empresa, "limit": limit}
        if numero_cuenta:
            params["numero_cuenta"] = numero_cuenta
        if con_match is not None:
            params["con_match"] = con_match
        return self._get("/v1/cuentas_bancarias/movimientos/", params)
    
    def matches(
        self, 
        rut_empresa: str, 
        numero_cuenta: Optional[str] = None
    ) -> Dict:
        """Lista conciliaciones (matches)"""
        params = {"rut_empresa": rut_empresa}
        if numero_cuenta:
            params["numero_cuenta"] = numero_cuenta
        return self._get("/v1/cuentas_bancarias/matches/", params)
    
    # =========================================================================
    # CONTABILIDAD
    # =========================================================================
    
    def plan_cuentas(self, rut_empresa: str, nivel: Optional[int] = None) -> Dict:
        """Obtiene el plan de cuentas"""
        params = {"rut_empresa": rut_empresa}
        if nivel:
            params["nivel"] = nivel
        return self._get("/v1/contabilidad/plan_cuenta/", params)
    
    def balance(
        self, 
        rut_empresa: str, 
        fecha_desde: str = "2025-01-01",
        tipo: Optional[str] = None
    ) -> Dict:
        """Obtiene balance de 8 columnas"""
        params = {
            "rut_empresa": self.normalize_rut(rut_empresa),
            "fecha_desde": fecha_desde
        }
        if tipo:
            params["tipo"] = tipo
        return self._get("/v1/contabilidad/balance/", params)
    
    def estado_resultados(self, rut_empresa: str, anio: int) -> Dict:
        """Obtiene estado de resultados"""
        return self._get("/v1/contabilidad/eerr/", {
            "rut_empresa": rut_empresa, "anio": anio
        })
    
    def libro_diario(
        self, 
        rut_empresa: str, 
        fecha_desde: Optional[str] = None,
        ordenar_por: Optional[str] = None
    ) -> Dict:
        """Obtiene libro diario"""
        params = {"rut_empresa": rut_empresa}
        if fecha_desde:
            params["fecha_desde"] = fecha_desde
        if ordenar_por:
            params["ordenar_por"] = ordenar_por
        return self._get("/v1/contabilidad/libro_diario/", params)
    
    def libro_mayor(self, rut_empresa: str, cuenta: str) -> Dict:
        """Obtiene libro mayor de una cuenta"""
        return self._get("/v1/contabilidad/libro_mayor/", {
            "rut_empresa": self.normalize_rut(rut_empresa), 
            "cuenta": cuenta
        })
    
    # =========================================================================
    # CLIENTES Y PROVEEDORES
    # =========================================================================
    
    def clientes_proveedores(
        self, 
        rut_empresa: str, 
        cliente: Optional[bool] = None
    ) -> Dict:
        """Lista clientes y proveedores"""
        params = {"rut_empresa": rut_empresa}
        if cliente is not None:
            params["cliente"] = cliente
        return self._get("/v1/companias/clientes_proveedores/", params)
    
    # =========================================================================
    # CONEXIONES
    # =========================================================================
    
    def listar_conexiones(self, rut_empresa: str) -> Dict:
        """Lista conexiones bancarias/SII"""
        return self._get("/v1/conexiones/", {"rut_empresa": rut_empresa})


def test_connection():
    """Prueba la conexión a Clay y lista empresas"""
    print("=" * 60)
    print("   TEST CONEXIÓN CLAY API")
    print("=" * 60)
    
    try:
        client = ClayClient()
        print(f"✅ Token configurado: {client.token[:20]}...")
        
        print("\n📊 Obteniendo empresas...")
        empresas = client.listar_empresas()
        
        # Estructura: {"status": True, "data": {"records": {...}, "items": [...]}}
        if empresas.get("status") and "data" in empresas:
            items = empresas["data"].get("items", [])
            total = empresas["data"].get("records", {}).get("total_records", len(items))
            print(f"✅ {total} empresas encontradas:\n")
            
            for i, emp in enumerate(items, 1):
                rut = f"{emp.get('rut', 'N/A')}-{emp.get('dv', '?')}"
                nombre = emp.get("real_name", emp.get("name", "N/A"))
                estado = emp.get("plan", {}).get("state", "N/A")
                print(f"   {i}. {rut:12} | {nombre[:40]:40} | {estado}")
            
            return items
        elif "items" in empresas:
            # Formato alternativo
            items = empresas["items"]
            print(f"✅ {len(items)} empresas encontradas")
            return items
        else:
            print(f"⚠️ Respuesta inesperada: {str(empresas)[:200]}")
            return []
            
    except ValueError as e:
        print(f"❌ Error de configuración: {e}")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e}")
        print(f"   Respuesta: {e.response.text[:200] if e.response else 'N/A'}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


if __name__ == "__main__":
    test_connection()
