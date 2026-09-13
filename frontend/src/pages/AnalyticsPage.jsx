import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { downloadCsv, getAnalytics } from '../services/analytics';
import './Milestone4.css';

function MetricCard({ label, value, footer, accent = 'var(--accent-purple)' }) {
  return (
    <div className="glass-card m4-card">
      <div className="m4-card-label">
        <span style={{ width: 8, height: 8, borderRadius: '50%', background: accent, display: 'inline-block' }} />
        {label}
      </div>
      <div className="m4-card-value">{value}</div>
      <div className="m4-card-sub"><span>{footer}</span></div>
    </div>
  );
}

export default function AnalyticsPage({ onNavigateToGaps }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getAnalytics());
    } catch (err) {
      setError(err?.message || 'Unable to load analytics data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = window.setInterval(load, 30000);
    return () => window.clearInterval(interval);
  }, [load]);

  const total = data?.summary?.totalQueries?.value ?? 0;
  const answered = data?.summary?.answeredQueries?.value ?? 0;
  const unanswered = data?.summary?.unansweredQueries?.value ?? 0;
  const avgConfidence = data?.summary?.avgConfidence?.value;
  const avgResponseTime = data?.summary?.avgResponseTime?.value;
  const answerRate = total > 0 ? (answered / total) * 100 : 0;

  const handleExport = useMemo(() => () => {
    if (!data) return;
    downloadCsv('querynest-analytics.csv', [
      ['metric', 'value'],
      ['total_queries', total],
      ['answered_queries', answered],
      ['unanswered_queries', unanswered],
      ['answer_rate_pct', answerRate.toFixed(2)],
      ['average_confidence_pct', avgConfidence == null ? '' : avgConfidence.toFixed(2)],
      ['average_response_time_seconds', avgResponseTime ?? ''],
      ...data.queryTypes.map((item) => [`query_type:${item.label}`, item.count]),
    ]);
  }, [data, total, answered, unanswered, answerRate, avgConfidence, avgResponseTime]);

  if (loading) {
    return <div className="m4-page"><div className="glass-panel m4-state"><h3>Loading analytics…</h3><p>Fetching real Milestone 4 telemetry from the backend.</p></div></div>;
  }

  if (error) {
    return <div className="m4-page"><div className="glass-panel m4-state"><h3>Unable to load analytics data.</h3><p>{error}</p><button className="btn btn-primary" onClick={load}>Retry</button></div></div>;
  }

  return (
    <div className="m4-page">
      <div className="m4-header-row">
        <div>
          <p style={{ fontSize: '0.65rem', fontWeight: 800, letterSpacing: '0.12em', color: 'var(--accent-emerald)', margin: '0 0 6px' }}>
            MILESTONE 4 · BACKEND TELEMETRY
          </p>
          <h1 className="m4-title">Analytics Dashboard</h1>
          <p className="m4-subtitle">Real query analytics collected by the QueryNest backend.</p>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={load}>⟳ Refresh</button>
          <button className="btn btn-primary" onClick={handleExport}>⬇ Export CSV</button>
        </div>
      </div>

      <div className="m4-cards">
        <MetricCard label="💬 Total Queries" value={total.toLocaleString()} footer="All recorded analytics" />
        <MetricCard label="✅ Answered" value={answered.toLocaleString()} footer={`${answerRate.toFixed(1)}% answer rate`} accent="var(--accent-emerald)" />
        <MetricCard label="🛡 Average Confidence" value={avgConfidence == null ? '—' : `${avgConfidence.toFixed(1)}%`} footer="Mean response confidence" accent="var(--accent-blue)" />
        <MetricCard label="⚠ Knowledge Gaps / Unanswered" value={unanswered.toLocaleString()} footer="Unanswered query events" accent="var(--accent-rose)" />
      </div>

      <div className="m4-grid-2">
        <div className="glass-panel m4-panel">
          <div className="m4-panel-head">
            <div><h3 className="m4-panel-title">Query Type Distribution</h3><p className="m4-panel-sub">Actual query classifications recorded by the backend.</p></div>
          </div>
          {data.queryTypes.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No query-type analytics recorded yet.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {data.queryTypes.map((item) => (
                <div key={item.label}>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      marginBottom: 6,
                      fontSize: '0.78rem',
                    }}
                  >
                    <strong>{item.label}</strong>
                    <span>{item.count} queries · {item.pct.toFixed(1)}%</span>
                  </div>

                  <div className="m4-bar-track">
                    <div
                      className="m4-bar-fill"
                      style={{
                        width: `${Math.min(100, item.pct)}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="glass-panel m4-panel">
          <div className="m4-panel-head">
            <div><h3 className="m4-panel-title">System Performance</h3><p className="m4-panel-sub">Metrics available from the current M4 backend.</p></div>
          </div>
          {[
            { label: 'Answer Rate', value: `${answerRate.toFixed(1)}%`, pct: answerRate },
            { label: 'Average Confidence', value: avgConfidence == null ? '—' : `${avgConfidence.toFixed(1)}%`, pct: avgConfidence ?? 0 },
          ].map((metric) => (
            <div key={metric.label} style={{ marginBottom: 18 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: 6 }}>
                <span>{metric.label}</span><strong>{metric.value}</strong>
              </div>
              <div className="m4-bar-track"><div className="m4-bar-fill" style={{ width: `${Math.max(0, Math.min(100, metric.pct))}%` }} /></div>
            </div>
          ))}
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', paddingTop: 8, borderTop: '1px solid var(--border-color)' }}>
            <span>Average response time</span><strong>{avgResponseTime == null ? '—' : `${Number(avgResponseTime).toFixed(3)} s`}</strong>
          </div>
        </div>
      </div>

      <div className="glass-panel m4-panel">
        <div className="m4-panel-head">
          <div><h3 className="m4-panel-title">Knowledge Gap Monitoring</h3><p className="m4-panel-sub">Open backend-detected gaps are available in the dedicated dashboard.</p></div>
          <button className="btn btn-secondary" onClick={onNavigateToGaps}>View Knowledge Gaps →</button>
        </div>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
          The dashboard deliberately avoids inventing unsupported daily trends, semantic topic clusters, or grounding percentages.
        </div>
      </div>
    </div>
  );
}
