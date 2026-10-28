// =============================================================================
// PrecalificaGT — Prueba de carga con k6 (E14), verificación de RNF-01 y RNF-02
//
// Escenario: rampa de 0 a 50 usuarios virtuales en 1 minuto, 50 VU sostenidos durante
// 5 minutos y bajada de 30 segundos, contra el ambiente desplegado en Render.
// Endpoints críticos: POST /api/simulador (RF-05) y POST /api/auth/login (RF-03).
//
// Ejecución (desde la raíz del repositorio):
//   k6 run -e BASE_URL=https://precalificagt-api.onrender.com tests/carga/carga_precalificagt.js
// Resultados: consola + reports/k6_resumen.json + reports/k6_resumen.md
// =============================================================================
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';

const BASE_URL = (__ENV.BASE_URL || 'https://precalificagt-api.onrender.com').replace(/\/$/, '');
const EMAIL = __ENV.EMAIL || 'cliente.demo@correo.com';
const PASSWORD = __ENV.PASSWORD || 'Cliente#2026';

// Métricas por endpoint
const duracionSimulador = new Trend('duracion_simulador', true);
const duracionLogin = new Trend('duracion_login', true);
const erroresSimulador = new Rate('errores_simulador');
const erroresLogin = new Rate('errores_login');
const respuestas5xx = new Counter('respuestas_5xx');

export const options = {
  scenarios: {
    rampa_50_vu: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: __ENV.RAMPA || '1m', target: 50 },      // rampa 0 → 50 VU
        { duration: __ENV.SOSTENIDO || '5m', target: 50 },  // 50 VU sostenidos durante 5 minutos
        { duration: '30s', target: 0 },                      // bajada
      ],
      gracefulRampDown: '30s',
    },
  },
  // Criterios de RNF-01 (p95 ≤ 2,000 ms y error < 1 %) y RNF-02 (< 1 % de 5xx)
  thresholds: {
    'http_req_duration{endpoint:simulador}': ['p(95)<=2000'],
    'http_req_duration{endpoint:login}': ['p(95)<=2000'],
    http_req_failed: ['rate<0.01'],
    errores_simulador: ['rate<0.01'],
    errores_login: ['rate<0.01'],
  },
  summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)', 'max'],
};

const JSON_HEADERS = { headers: { 'Content-Type': 'application/json', Accept: 'application/json' } };
const PRODUCTOS = [
  { producto_codigo: 'PERSONAL', monto: 50000, plazo_meses: 36 },
  { producto_codigo: 'VEHICULAR', monto: 120000, plazo_meses: 60 },
  { producto_codigo: 'HIPOTECARIO', monto: 600000, plazo_meses: 240 },
];

// Despierta el servicio gratuito antes de medir (Render lo suspende tras 15 min sin tráfico)
export function setup() {
  for (let intento = 1; intento <= 12; intento++) {
    const r = http.get(`${BASE_URL}/api/health`, { timeout: '90s' });
    if (r.status === 200) {
      console.log(`API lista (intento ${intento}): ${r.body}`);
      return;
    }
    sleep(5);
  }
  throw new Error(`La API ${BASE_URL} no respondió a /api/health`);
}

export default function () {
  const datos = PRODUCTOS[Math.floor(Math.random() * PRODUCTOS.length)];
  const sim = http.post(`${BASE_URL}/api/simulador`, JSON.stringify(datos),
    { ...JSON_HEADERS, tags: { endpoint: 'simulador' } });
  const simOk = check(sim, {
    'simulador: HTTP 200': (r) => r.status === 200,
    'simulador: trae cuota_mensual': (r) => r.status === 200 && r.json('cuota_mensual') > 0,
  });
  duracionSimulador.add(sim.timings.duration);
  erroresSimulador.add(!simOk);
  if (sim.status >= 500) respuestas5xx.add(1);

  sleep(1);

  const login = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({ email: EMAIL, password: PASSWORD }),
    { ...JSON_HEADERS, tags: { endpoint: 'login' } });
  const loginOk = check(login, {
    'login: HTTP 200': (r) => r.status === 200,
    'login: trae token': (r) => r.status === 200 && typeof r.json('token') === 'string',
  });
  duracionLogin.add(login.timings.duration);
  erroresLogin.add(!loginOk);
  if (login.status >= 500) respuestas5xx.add(1);

  sleep(1);
}

function fila(nombre, trend, errores, m) {
  const t = m[trend] ? m[trend].values : {};
  const e = m[errores] ? m[errores].values.rate * 100 : 0;
  const cumple = (t['p(95)'] || 0) <= 2000 && e < 1;
  return `| ${nombre} | ${(t.avg || 0).toFixed(0)} ms | ${(t['p(95)'] || 0).toFixed(0)} ms | ` +
         `${(t.max || 0).toFixed(0)} ms | ${e.toFixed(2)} % | ${cumple ? 'Cumple' : 'No cumple'} |`;
}

export function handleSummary(data) {
  const m = data.metrics;
  const duracionSeg = data.state.testRunDurationMs / 1000;
  const reqs = m.http_reqs.values.count;
  const md = [
    '# Resultados de la prueba de carga (k6)',
    '',
    `- Ambiente: ${BASE_URL}`,
    `- Duración: ${duracionSeg.toFixed(0)} s · VU máximos: ${m.vus_max.values.max}`,
    `- Solicitudes: ${reqs} · Throughput: ${m.http_reqs.values.rate.toFixed(2)} req/s`,
    `- Tasa de error HTTP global: ${(m.http_req_failed.values.rate * 100).toFixed(2)} % · Respuestas 5xx: ${m.respuestas_5xx ? m.respuestas_5xx.values.count : 0}`,
    `- Tiempo de respuesta global: promedio ${m.http_req_duration.values.avg.toFixed(0)} ms, p95 ${m.http_req_duration.values['p(95)'].toFixed(0)} ms`,
    '',
    '| Endpoint | Promedio | p95 | Máximo | Error | RNF-01 (p95 ≤ 2,000 ms y error < 1 %) |',
    '|---|---|---|---|---|---|',
    fila('POST /api/simulador', 'duracion_simulador', 'errores_simulador', m),
    fila('POST /api/auth/login', 'duracion_login', 'errores_login', m),
    '',
  ].join('\n');
  return {
    stdout: md + '\n',
    'reports/k6_resumen.md': md,
    'reports/k6_resumen.json': JSON.stringify(data, null, 2),
  };
}
