/**
 * Balance Tributario + Análisis por Cuenta a Excel
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
  
  if (!response.ok) return null;
  return await response.json();
}

async function getBalance(tenantRut, idPeriodo) {
  return await apiGet(tenantRut, `/contabilidad/reportes/balancetributario/${idPeriodo}`);
}

async function getAnalisisCuenta(tenantRut, idCuenta, fechaCorte) {
  return await apiGet(tenantRut, `/contabilidad/reportes/analisisporcuenta/${idCuenta}?fechaCorte=${fechaCorte}&soloPendientes=false`);
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

function createCuentaSheet(data) {
  if (!data || !Array.isArray(data) || data.length === 0) return null;

  const rows = data.map(mov => ({
    'Fecha': mov.fecha ? mov.fecha.substring(0, 10) : '',
    'Comprobante': mov.numero,
    'Tipo': mov.tipo,
    'Auxiliar': mov.auxiliar || mov.idAuxiliar || '',
    'Glosa': mov.glosa,
    'Debe': mov.debe,
    'Haber': mov.haber,
    'Saldo': mov.saldo
  }));

  const ws = XLSX.utils.json_to_sheet(rows);
  ws['!cols'] = [
    { wch: 12 }, { wch: 12 }, { wch: 8 }, { wch: 25 },
    { wch: 40 }, { wch: 15 }, { wch: 15 }, { wch: 15 }
  ];
  return ws;
}

function sanitizeSheetName(codigo, nombre) {
  // Excel max 31 chars
  const clean = `${codigo} ${nombre}`.replace(/[\\\/\*\?\[\]:]/g, '').substring(0, 31);
  return clean;
}

async function main() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('   BALANCE + ANÁLISIS POR CUENTA A EXCEL');
  console.log('═══════════════════════════════════════════════════════════');

  const tenantKey = 'FIDI';
  const tenant = tenants[tenantKey];
  const idPeriodo = '202511';
  const fechaCorte = '2025-11-30';

  const wb = XLSX.utils.book_new();
  const sheetNames = new Set();

  // 1. Obtener Balance
  console.log('\n📊 Obteniendo Balance Tributario...');
  const balance = await getBalance(tenant.rut, idPeriodo);
  if (!balance) {
    console.log('   ❌ Error obteniendo balance');
    return;
  }
  
  // Filtrar cuentas con saldo != 0
  const balanceFiltrado = balance.filter(c => 
    c.deudor !== 0 || c.acreedor !== 0 || 
    c.activos !== 0 || c.pasivos !== 0 || 
    c.perdidas !== 0 || c.ganancias !== 0
  );
  
  const wsBalance = createBalanceSheet(balanceFiltrado);
  XLSX.utils.book_append_sheet(wb, wsBalance, 'Balance Tributario');
  sheetNames.add('Balance Tributario');
  console.log(`   ✅ ${balanceFiltrado.length} cuentas (de ${balance.length} totales)`);

  // 2. Para cada cuenta con saldo, obtener análisis
  console.log('\n📋 Procesando cuentas con movimientos...');
  let cuentasConDatos = 0;

  for (const cuenta of balanceFiltrado) {
    const analisis = await getAnalisisCuenta(tenant.rut, cuenta.idCuenta, fechaCorte);
    
    if (analisis && Array.isArray(analisis) && analisis.length > 0) {
      let sheetName = sanitizeSheetName(cuenta.idCuenta, cuenta.cuenta);
      
      // Evitar duplicados
      let suffix = 1;
      let originalName = sheetName;
      while (sheetNames.has(sheetName)) {
        sheetName = `${originalName.substring(0, 28)}_${suffix}`;
        suffix++;
      }
      
      const wsCuenta = createCuentaSheet(analisis);
      if (wsCuenta) {
        XLSX.utils.book_append_sheet(wb, wsCuenta, sheetName);
        sheetNames.add(sheetName);
        cuentasConDatos++;
        console.log(`   ✅ ${cuenta.idCuenta}: ${analisis.length} movimientos`);
      }
    }
  }

  console.log(`\n   📊 Cuentas con datos: ${cuentasConDatos}`);

  // 3. Guardar
  const filename = `Balance_PorCuenta_${tenantKey}_${idPeriodo}.xlsx`;
  XLSX.writeFile(wb, filename);
  console.log(`\n💾 Guardado: ${filename}`);

  console.log('\n═══════════════════════════════════════════════════════════');
}

main();

