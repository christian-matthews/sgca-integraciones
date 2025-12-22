/**
 * Exactamente como la documentación
 */

require('dotenv').config();
const fs = require('fs');

const TOKEN = process.env.SKUALO_API_TOKEN;

async function main() {
  const url = "https://api.skualo.cl/77285542-7/contabilidad/reportes/resultados?fechaCorte=2025-12-31&agrupadoPor=0&incluyeAjusteTributario=false";
  
  console.log('URL:', url);
  console.log('Token:', TOKEN.substring(0, 20) + '...');
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'accept': 'application/json',
      'Authorization': `Bearer ${TOKEN}`
    }
  });

  console.log('Status:', response.status);
  const text = await response.text();
  console.log('Response:', text);
}

main();
