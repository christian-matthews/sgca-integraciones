/**
 * Probar reportes con períodos que tienen datos
 */

require('dotenv').config();
const fs = require('fs');

const API_BASE = 'https://api.skualo.cl';
const TOKEN = process.env.SKUALO_API_TOKEN;
const tenants = JSON.parse(fs.readFileSync('./tenants.json', 'utf8'));
const tenant = tenants['CISI'];

async function testEndpoint(path, showBody = false) {
  const url = `${API_BASE}/${tenant.rut}${path}`;
  
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'Accept': 'application/json'
      }
    });

    const status = response.status;
    const statusIcon = status === 200 ? '✅' : status === 404 ? '❌' : '⚠️';
    
    const data = await response.json().catch(() => ({}));
    
    let detail = data.detail || data.title || '';
    console.log(`${statusIcon} ${status} | ${path}`);
    if (detail) console.log(`   → ${detail.substring(0, 100)}`);
    
    if (response.ok) {
      if (showBody) {
        const preview = JSON.stringify(data, null, 2).substring(0, 800);
        console.log(`   ${preview}...`);
      }
      const filename = `cisi${path.replace(/\//g, '_').replace(/\?/g, '_').replace(/=/g, '_').replace(/&/g, '_')}.json`;
      fs.writeFileSync(filename, JSON.stringify(data, null, 2));
      console.log(`   💾 Guardado: ${filename}`);
    }
    
    return { ok: response.ok, data, status };
  } catch (error) {
    console.log(`💥 ERR | ${path} - ${error.message}`);
    return { ok: false };
  }
}

async function main() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('   PROBANDO CON PERÍODOS CON DATOS');
  console.log('   Tenant: ' + tenant.rut);
  console.log('═══════════════════════════════════════════════════════════\n');

  // Probar con diferentes períodos - sabemos que hay comprobantes desde oct 2024
  const endpoints = [
    // Libro Mayor - período completo 2024
    '/contabilidad/reportes/libromayor?Desde=2024-01-01&Hasta=2024-12-31',
    '/contabilidad/reportes/libromayor?Desde=2024-10-01&Hasta=2024-12-31',
    '/contabilidad/reportes/libromayor?Desde=2025-01-01&Hasta=2025-12-31',
    
    // Libro Diario
    '/contabilidad/reportes/librodiario?Desde=2024-10-01&Hasta=2024-12-31',
    '/contabilidad/reportes/librodiario?Desde=2025-01-01&Hasta=2025-06-30',
  ];

  for (const endpoint of endpoints) {
    const result = await testEndpoint(endpoint, true);
    if (result.ok) {
      console.log('\n🎉 ¡ÉXITO!\n');
    }
    await new Promise(r => setTimeout(r, 300));
  }

  console.log('\n═══════════════════════════════════════════════════════════');
}

main();
