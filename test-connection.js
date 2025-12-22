/**
 * Test de conexión a la API de Skualo
 */

require('dotenv').config();
const fs = require('fs');

// Configuración
const API_BASE = 'https://api.skualo.cl';
const TOKEN = process.env.SKUALO_API_TOKEN;

// Cargar tenants
const tenants = JSON.parse(fs.readFileSync('./tenants.json', 'utf8'));

async function testConnection(tenantKey) {
  const tenant = tenants[tenantKey];
  
  if (!tenant) {
    console.error(`❌ Tenant "${tenantKey}" no encontrado en tenants.json`);
    return false;
  }

  const url = `${API_BASE}/${tenant.rut}/empresa`;
  
  console.log(`\n🔄 Probando conexión para: ${tenant.nombre} (${tenant.rut})`);
  console.log(`   URL: ${url}`);

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'Accept': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      console.log(`✅ Conexión exitosa!`);
      console.log(`   Empresa: ${data.razon_social || data.nombre || 'N/A'}`);
      console.log(`   Status: ${response.status}`);
      return true;
    } else {
      const errorText = await response.text();
      console.error(`❌ Error ${response.status}: ${response.statusText}`);
      console.error(`   Respuesta: ${errorText}`);
      return false;
    }
  } catch (error) {
    console.error(`❌ Error de conexión: ${error.message}`);
    return false;
  }
}

async function main() {
  console.log('═══════════════════════════════════════');
  console.log('   TEST DE CONEXIÓN - API SKUALO');
  console.log('═══════════════════════════════════════');

  // Verificar token
  if (!TOKEN) {
    console.error('\n❌ SKUALO_API_TOKEN no está definido en .env');
    process.exit(1);
  }
  console.log(`\n🔑 Token: ${TOKEN.substring(0, 10)}...`);

  // Probar cada tenant activo
  const activeTenantsKeys = Object.keys(tenants).filter(key => tenants[key].activo);
  
  console.log(`\n📋 Tenants activos: ${activeTenantsKeys.length}`);

  for (const key of activeTenantsKeys) {
    await testConnection(key);
  }

  console.log('\n═══════════════════════════════════════\n');
}

main();

