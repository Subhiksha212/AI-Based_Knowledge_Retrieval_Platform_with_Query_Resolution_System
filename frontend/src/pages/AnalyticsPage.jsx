import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  downloadCsv,
  getAnalytics,
  getQueryThemes,
} from '../services/analytics';
import './Milestone4.css';

function MetricCard({ label, value, footer, accent = 'var(--accent-purple)' }) {
  return (
    <div className="glass-card m4-card">
      <div className="m4-card-label">
        <span
          style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: accent,
            display: 'inline-block',
          }}
        />
        {label}
      </div>
      <div className="m4-card-value">{value}</div>
      <div className="m4-card-sub"><span>{footer}</span></div>
    </div>
  );
}

export default function AnalyticsPage({ onNavigateToGaps }) {
  const [data, setData] = useState(null);
  const [queryThemes, setQueryThemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [themesLoading, setThemesLoading] = useState(true);
  const [error, setError] = useState(null);
  const [themesError, setThemesError] = useState(null);

  const loadThemes = useCallback(async () => {
    setThemesLoading(true);
    setThemesError(null);

    try {
      const themes = await getQueryThemes();
      setQueryThemes(themes);
    } catch (err) {
      setThemesError(err?.message || 'Unable to load common query themes.');
      setQueryThemes([]);
    } finally {
      setThemesLoading(false);
    }
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Fast dashboard metrics load independently from semantic themes.
      const analyticsData = await getAnalytics();
      setData(analyticsData);

      // Start theme calculation only after the main dashboard data is ready.
      // It no longer blocks the first render of the dashboard.
      void loadThemes();
    } catch (err) {
      setError(err?.message || 'Unable to load analytics data.');
    } finally {
      setLoading(false);
    }
  }, [loadThemes]);

  useEffect(() => {
    load();
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
      [
        'average_confidence_pct',
        avgConfidence == null ? '' : avgConfidence.toFixed(2),
      ],
      ['average_response_time_seconds', avgResponseTime ?? ''],
      ...data.queryTypes.map((item) => [
        `query_type:${item.label}`,
        item.count,
      ]),
      ['section', 'common_query_themes'],
      [
        'theme',
        'query_count',
        'unanswered',
        'low_confidence',
        'average_confidence_pct',
        'gap_score_pct',
        'knowledge_gap',
      ],
      ...queryThemes.map((item) => [
        item.theme,
        item.query_count,
        item.unanswered_count,
        item.low_confidence_count,
        item.average_confidence == null
          ? ''
          : (item.average_confidence * 100).toFixed(1),
        (item.gap_score * 100).toFixed(1),
        item.knowledge_gap ? 'yes' : 'no',
      ]),
    ]);
  }, [
    data,
    total,
    answered,
    unanswered,
    answerRate,
    avgConfidence,
    avgResponseTime,
    queryThemes,
  ]);

  if (loading) {
    return (
      <div className="m4-page">
        <div className="glass-panel m4-state">
          <h3>Loading analytics…</h3>
          <p>Gathering the latest analytics and insights</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="m4-page">
        <div className="glass-panel m4-state">
          <h3>Unable to load analytics data.</h3>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={load}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="m4-page">
      <div className="m4-header-row">
        <div>
          <h1 className="m4-title">Analytics Dashboard</h1>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={load}>
            ⟳ Refresh
          </button>
          <button className="btn btn-primary" onClick={handleExport}>
            ⬇ Export CSV
          </button>
        </div>
      </div>

      <div className="m4-cards">
        <MetricCard
          label="💬 Total Queries"
          value={total.toLocaleString()}
          footer="All recorded analytics"
        />
        <MetricCard
          label="✅ Answered"
          value={answered.toLocaleString()}
          footer={`${answerRate.toFixed(1)}% answer rate`}
          accent="var(--accent-emerald)"
        />
        <MetricCard
          label="🛡 Average Confidence"
          value={avgConfidence == null ? '—' : `${avgConfidence.toFixed(1)}%`}
          footer="Mean response confidence"
          accent="var(--accent-blue)"
        />
        <MetricCard
          label="⚠ Knowledge Gaps / Unanswered"
          value={unanswered.toLocaleString()}
          footer="Unanswered query events"
          accent="var(--accent-rose)"
        />
      </div>

      <div className="m4-grid-2">
        <div className="glass-panel m4-panel">
          <div className="m4-panel-head">
            <div><h3 className="m4-panel-title">Query Type Distribution</h3></div>
          </div>
          {data.queryTypes.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>
              No query-type analytics recorded yet.
            </p>
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
            <div><h3 className="m4-panel-title">System Performance</h3></div>
          </div>
          {[
            {
              label: 'Answer Rate',
              value: `${answerRate.toFixed(1)}%`,
              pct: answerRate,
            },
            {
              label: 'Average Confidence',
              value: avgConfidence == null ? '—' : `${avgConfidence.toFixed(1)}%`,
              pct: avgConfidence ?? 0,
            },
          ].map((metric) => (
            <div key={metric.label} style={{ marginBottom: 18 }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: '0.78rem',
                  marginBottom: 6,
                }}
              >
                <span>{metric.label}</span><strong>{metric.value}</strong>
              </div>
              <div className="m4-bar-track">
                <div
                  className="m4-bar-fill"
                  style={{
                    width: `${Math.max(0, Math.min(100, metric.pct))}%`,
                  }}
                />
              </div>
            </div>
          ))}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: '0.8rem',
              paddingTop: 8,
              borderTop: '1px solid var(--border-color)',
            }}
          >
            <span>Average response time</span>
            <strong>
              {avgResponseTime == null
                ? '—'
                : `${Number(avgResponseTime).toFixed(3)} s`}
            </strong>
          </div>
        </div>
      </div>

      <div className="glass-panel m4-panel">
        <div className="m4-panel-head">
          <div>
            <h3 className="m4-panel-title">Common Query Themes</h3>
          </div>
        </div>

        {themesLoading ? (
          <p style={{ color: 'var(--text-muted)' }}>
            Analyzing common query themes…
          </p>
        ) : themesError ? (
          <div>
            <p style={{ color: 'var(--text-muted)' }}>
              Common query themes could not be loaded right now.
            </p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.78rem' }}>
              {themesError}
            </p>
            <button className="btn btn-secondary" onClick={loadThemes}>
              Retry Themes
            </button>
          </div>
        ) : queryThemes.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>
            No query-theme data is available yet. Submit a few queries to build semantic themes.
          </p>
        ) : (
          <div className="m4-theme-grid">
            {queryThemes.slice(0, 8).map((theme) => (
              <div
                key={`${theme.theme}-${theme.representative_query}`}
                className={`m4-theme-card ${theme.knowledge_gap ? 'gap' : ''}`}
              >
                <div className="m4-theme-top">
                  <strong>{theme.theme}</strong>
                  <span className={`m4-status ${theme.knowledge_gap ? 'warn' : 'ok'}`}>
                    {theme.knowledge_gap ? '⚠ Knowledge Gap' : '✓ Healthy'}
                  </span>
                </div>
                <div className="m4-theme-query">“{theme.representative_query}”</div>
                <div className="m4-theme-stats">
                  <span>{theme.query_count} queries</span>
                  <span>{theme.unanswered_count} unanswered</span>
                  <span>{theme.low_confidence_count} low confidence</span>
                  <span>{(theme.gap_score * 100).toFixed(0)}% gap score</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="glass-panel m4-panel">
        <div className="m4-panel-head">
          <div><h3 className="m4-panel-title">Knowledge Gap Monitoring</h3></div>
          <button className="btn btn-secondary" onClick={onNavigateToGaps}>
            View Knowledge Gaps →
          </button>
        </div>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
          Common query themes are analyzed separately from RAG retrieval and
          are loaded independently so they do not block the main analytics dashboard.
        </div>
      </div>
    </div>
  );
}
