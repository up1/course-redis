// k6 run -e PATH_PREFIX=/api/user/db perf/load.js   (PostgreSQL only)
// k6 run -e PATH_PREFIX=/api/user    perf/load.js   (Redis + PostgreSQL)
import http from 'k6/http';
import { check } from 'k6';

const BASE = __ENV.BASE_URL || 'http://localhost:8080';
const PREFIX = __ENV.PATH_PREFIX || '/api/user';
const HOT_IDS = parseInt(__ENV.HOT_IDS || '1000');   // working set -> cache hit ratio ~100% after warm-up

export const options = {
  vus: parseInt(__ENV.VUS || '50'),
  duration: __ENV.DURATION || '20s',
  summaryTrendStats: ['avg', 'med', 'p(90)', 'p(95)', 'max'],
};

export default function () {
  const id = 1 + Math.floor(Math.random() * HOT_IDS);
  const res = http.get(`${BASE}${PREFIX}/${id}`);
  check(res, { 'status 200': (r) => r.status === 200 });
}
