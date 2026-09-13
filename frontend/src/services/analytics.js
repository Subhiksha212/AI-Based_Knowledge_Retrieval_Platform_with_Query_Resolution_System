/*
 * QueryNest Milestone 4 Analytics Service
 *
 * Uses the ACTUAL FastAPI M4 endpoints. No fabricated mock analytics are
 * returned here because the backend already provides real telemetry.
 */

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/$/, '');

const getToken = () =>
  localStorage.getItem('qn_auth_token') ||
  sessionStorage.getItem('qn_auth_token');

const authHeaders = () => {
  const headers = { Accept: 'application/json' };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
};

async function fetchJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: authHeaders(),
  });

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const detail = data?.detail || data?.message || `HTTP ${response.status}`;
    throw new Error(detail);
  }

  return data;
}

export const DATE_RANGES = [
  { id: 'all', label: 'All Recorded Data' },
];

function confidencePercent(value) {
  if (value == null || Number.isNaN(Number(value))) return null;
  return Math.max(0, Math.min(100, Number(value) * 100));
}

export async function getAnalytics() {
  const [overview, queryTypes] = await Promise.all([
    fetchJson('/analytics/overview'),
    fetchJson('/analytics/query-types'),
  ]);

  const total = Number(overview?.total_queries || 0);
  const answered = Number(overview?.answered_queries || 0);
  const unanswered = Number(overview?.unanswered_queries || 0);
  const avgConfidence = confidencePercent(overview?.average_confidence);

  const typeRows = Array.isArray(queryTypes) ? queryTypes : [];
  const queryTypeData = typeRows
    .filter((row) => row?.query_type)
    .map((row) => ({
      label: String(row.query_type),
      count: Number(row.count || 0),
      pct: total > 0 ? (Number(row.count || 0) / total) * 100 : 0,
    }))
    .sort((a, b) => b.count - a.count);

  return {
    source: 'backend',
    range: 'all',
    rangeLabel: 'All Recorded Data',
    summary: {
      totalQueries: { value: total },
      answeredQueries: { value: answered },
      unansweredQueries: { value: unanswered },
      avgConfidence: { value: avgConfidence },
      avgResponseTime: { value: overview?.average_response_time ?? null },
    },
    queryTypes: queryTypeData,
  };
}

export async function getKnowledgeGaps() {
  const [gaps, top, statistics] = await Promise.all([
    fetchJson('/knowledge-gaps'),
    fetchJson('/knowledge-gaps/top'),
    fetchJson('/knowledge-gaps/statistics'),
  ]);

  return {
    source: 'backend',
    range: 'all',
    rangeLabel: 'All Recorded Data',
    gaps: Array.isArray(gaps) ? gaps : [],
    top: Array.isArray(top) ? top : [],
    statistics: statistics || {},
  };
}

export function downloadCsv(filename, rows) {
  const escape = (value) => `"${String(value ?? '').replace(/"/g, '""')}"`;
  const csv = rows.map((row) => row.map(escape).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
