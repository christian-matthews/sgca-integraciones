/**
 * Balance Tributario + Análisis por Auxiliar a Excel
 */

require('dotenv').config();
const fs = require('fs');
const XLSX = require('xlsx');

const API_BASE = 'https://api.skualo.cl';
const TOKEN = process.env.SKUALO_API_TOKEN;
const tenants = JSON.parse(fs.readFileSync('./tenants.json', 'utf8'));

async function apiGet(tenantRut, path) {
  const url = `${API_BASE}/${tenantRut}${path}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'accept': 'application/json'
    }
  });
  
  if (!response.ok) {
    return null;
  }
  return await response.json();
}

async function getBalance(tenantRut, idPeriodo) {
  return await apiGet(tenantRut, `/contabilidad/reportes/balancetributario/${idPeriodo}`);
}

async function getAuxiliares(tenantRut) {
  const response = await apiGet(tenantRut, '/auxiliares?PageSize=500');
  return response?.items || [];
}

async function getAnalisisAuxiliar(tenantRut, idAuxiliar, desde, hasta) {
  return await apiGet(tenantRut, `/contabilidad/reportes/analisisporauxiliar/${idAuxiliar}?Desde=${desde}&Hasta=${hasta}`);
}

function createBalanceSheet(data) {
  const rows = data.map(cuenta => ({
    'Código': cuenta.idCuenta,
    'Cuenta': cuenta.cuenta,
    'Débitos': cuenta.debitos,
    'Créditos': cuenta.creditos,
    'Saldo Deudor': cuenta.deudor,
    'Saldo Acreedor': cuenta.acreedor,
    'Activos': cuenta.activos,
    'Pasivos': cuenta.pasivos,
    'Pérdidas': cuenta.perdidas,
    'Ganancias': cuenta.ganancias
  }));

  const ws = XLSX.utils.json_to_sheet(rows);
  ws['!cols'] = [
    { wch: 12 }, { wch: 40 }, { wch: 15 }, { wch: 15 },
    { wch: 15 }, { wch: 15 }, { wch: 15 }, { wch: 15 },
    { wch: 15 }, { wch: 15 }
  ];
  return ws;
}

function createAuxiliarSheet(data, nombreAuxiliar) {
  if (!data || !Array.isArray(data) || data.length === 0) {
    return null;
  }

  const rows = data.map(mov => ({
    'Fecha': mov.fecha ? mov.fecha.substring(0, 10) : '',
    'Comprobante': mov.numero,
    'Tipo': mov.tipo,
    'Glosa': mov.glosa,
    'Cuenta': mov.cuenta,
    'Debe': mov.debe,
    'Haber': mov.haber,
    'Saldo': mov.saldo
  }));

  const ws = XLSX.utils.json_to_sheet(rows);
  ws['!cols'] = [
    { wch: 12 }, { wch: 12 }, { wch: 8 }, { wch: 40 },
    { wch: 30 }, { wch: 15 }, { wch: 15 }, { wch: 15 }
  ];
  return ws;
}

function sanitizeSheetName(name) {
  // Excel sheet names max 31 chars, no special chars
  return name
    .replace(/[\\\/\*\?\[\]:]/g, '')
    .substring(0, 31);
}

async function main() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('   BALANCE + AUXILIARES A EXCEL');
  console.log('═══════════════════════════════════════════════════════════');

  const tenantKey = 'FIDI';
  const tenant = tenants[tenantKey];
  const idPeriodo = '202511';
  const desde = '2025-01-01';
  const hasta = '2025-11-30';

  const wb = XLSX.utils.book_new();

  // 1. Obtener y agregar Balance
  console.log('\n📊 Obteniendo Balance Tributario...');
  const balance = await getBalance(tenant.rut, idPeriodo);
  if (balance) {
    const wsBalance = createBalanceSheet(balance);
    XLSX.utils.book_append_sheet(wb, wsBalance, 'Balance Tributario');
    console.log(`   ✅ ${balance.length} cuentas`);
  }

  // 2. Obtener lista de auxiliares
  console.log('\n👥 Obteniendo lista de auxiliares...');
  const auxiliares = await getAuxiliares(tenant.rut);
  
  if (!auxiliares || auxiliares.length === 0) {
    console.log('   ⚠️ No hay auxiliares');
  } else {
    console.log(`   ✅ ${auxiliares.length} auxiliares encontrados`);
    
    // 3. Para cada auxiliar, obtener análisis
    console.log('\n📋 Procesando auxiliares con movimientos...');
    let auxiliaresConDatos = 0;
    
    for (const aux of auxiliares) {
      const analisis = await getAnalisisAuxiliar(tenant.rut, aux.id, desde, hasta);
      
      if (analisis && Array.isArray(analisis) && analisis.length > 0) {
        const sheetName = sanitizeSheetName(aux.nombre || aux.id);
        const wsAux = createAuxiliarSheet(analisis, aux.nombre);
        
        if (wsAux) {
          try {
            XLSX.utils.book_append_sheet(wb, wsAux, sheetName);
            auxiliaresConDatos++;
            console.log(`   ✅ ${sheetName}: ${analisis.length} movimientos`);
          } catch (e) {
            // Nombre duplicado, agregar sufijo
            XLSX.utils.book_append_sheet(wb, wsAux, `${sheetName.substring(0, 28)}_${auxiliaresConDatos}`);
            auxiliaresConDatos++;
          }
        }
      }
    }
    
    console.log(`\n   📊 Auxiliares con datos: ${auxiliaresConDatos}`);
  }

  // 4. Guardar archivo
  const filename = `Balance_Auxiliares_${tenantKey}_${idPeriodo}.xlsx`;
  XLSX.writeFile(wb, filename);
  console.log(`\n💾 Guardado: ${filename}`);

  console.log('\n═══════════════════════════════════════════════════════════');
}

main();
