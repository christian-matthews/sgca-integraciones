/**
 * Obtener Balance Tributario de Skualo
 */

require('dotenv').config();
const fs = require('fs');

const API_BASE = 'https://api.skualo.cl';
const TOKEN = process.env.SKUALO_API_TOKEN;
const tenants = JSON.parse(fs.readFileSync('./tenants.json', 'utf8'));

async function getBalance(tenantKey, year, month) {
  const tenant = tenants[tenantKey];
  
  if (!tenant) {
    console.error(`❌ Tenant "${tenantKey}" no encontrado`);
    return null;
  }

  // Formatear mes con 2 dígitos
  const monthStr = month.toString().padStart(2, '0');
  const periodo = `${year}-${monthStr}`;

  const url = `${API_BASE}/${tenant.rut}/contabilidad/balance-tributario?periodo=${periodo}`;
  
  console.log(`\n🔄 Obteniendo Balance Tributario...`);
  console.log(`   Empresa: ${tenant.nombre}`);
  console.log(`   Período: ${periodo}`);
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
      console.log(`\n✅ Balance obtenido exitosamente!`);
      
      // Guardar JSON
      const filename = `balance_${tenantKey}_${periodo}.json`;
      fs.writeFileSync(filename, JSON.stringify(data, null, 2));
      console.log(`💾 Guardado en: ${filename}`);
      
      // Mostrar resumen
      if (Array.isArray(data)) {
        console.log(`📊 Total de cuentas: ${data.length}`);
      } else if (data.data && Array.isArray(data.data)) {
        console.log(`📊 Total de cuentas: ${data.data.length}`);
      }
      
      return data;
    } else {
      const errorText = await response.text();
      console.error(`\n❌ Error ${response.status}: ${response.statusText}`);
      console.error(`   Respuesta: ${errorText}`);
      return null;
    }
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`);
    return null;
  }
}

// Ejecutar: Balance de Noviembre 2024
getBalance('FIDI', 2024, 11);

