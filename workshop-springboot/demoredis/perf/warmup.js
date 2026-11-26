// Loads every user id (1..TOTAL) into Redis through GET /api/user/{id}
// k6 run perf/warmup.js
// k6 run -q -e TOTAL=1000 -e HOT_IDS=1000 perf/warmup.js 2>&1 | grep -E "http_req_failed|checks" ; for p in /api/user/db /api/user; do echo "== $p (pooled)"; k6 run -q -e PATH_PREFIX=$p -e VUS=100 -e DURATION=20s perf/load.js 2>&1 | grep -E "http_req_duration|http_reqs|http_req_failed"; done
import http from 'k6/http';
import { check } from 'k6';
import exec from 'k6/execution';

const TOTAL = parseInt(__ENV.TOTAL || '1000000');

export const options = {
  scenarios: {
    warmup: { executor: 'shared-iterations', vus: 50, iterations: TOTAL, maxDuration: '10m' },
  },
};

export default function () {
  const id = exec.scenario.iterationInTest + 1;
  const res = http.get(`${__ENV.BASE_URL || 'http://localhost:8080'}/api/user/${id}`);
  check(res, { 'status 200': (r) => r.status === 200 });
}
