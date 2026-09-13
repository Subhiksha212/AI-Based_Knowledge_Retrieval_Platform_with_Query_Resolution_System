import React, { useState, useEffect, useMemo } from 'react';
import * as api from '../services/api';
import './HistoryPage.css';

export default function HistoryPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [statistics, setStatistics] = useState({
    totalConversations: 0,
    totalQueries: 0,
    averageConfidence: 0,
    averageSources: 0,
  });

  const [historyFeed, setHistoryFeed] = useState([]);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      try {
        setIsLoading(true);
        setError(null);

        // 1. Fetch conversations metadata
        const convData = await api.getConversations();
        const userConversations = Array.isArray(convData?.conversations) 
          ? convData.conversations 
          : [];

        if (userConversations.length === 0) {
          if (isMounted) {
            setStatistics({
              totalConversations: 0,
              totalQueries: 0,
              averageConfidence: 0,
            });
            setHistoryFeed([]);
            setIsLoading(false);
          }
          return;
        }

        // 2. We limit fetching details to the top 20 most recent to avoid massive N+1.
        // The backend sorts by updated_at descending.
        const topConversations = userConversations.slice(0, 20);

        // 3. Fetch detailed messages for these top conversations in parallel
        const detailsPromises = topConversations.map(conv => 
          api.getConversation(conv.conversation_id).catch(err => {
            console.warn(`Failed to fetch details for ${conv.conversation_id}`, err);
            return null; // Handle individual fetch failures gracefully
          })
        );
        const detailedConversations = await Promise.all(detailsPromises);

        // 4. Calculate stats and build the feed
        let totalQueriesCount = 0;
        let confidenceSum = 0;
        let confidenceCount = 0;
        let sourcesSum = 0;
        let validSourcesQueries = 0;
        const feed = [];

        for (const detail of detailedConversations) {
          if (!detail || !Array.isArray(detail.messages)) continue;

          // Process messages for stats and feed mapping
          for (let i = 0; i < detail.messages.length; i++) {
            const msg = detail.messages[i];
            if (msg.role === 'user') {
              totalQueriesCount++;
              
              // Find the immediate next bot response
              const nextMsg = detail.messages[i + 1];
              let confidence = null;
              let sourcesCount = 0;
              let hasSources = false;
              let botResponseText = 'No response';

              if (nextMsg && nextMsg.role !== 'user') {
                botResponseText = nextMsg.content || 'No response';
                const metadata = nextMsg.message_metadata;
                
                if (metadata) {
                  // Some metadata might be stringified depending on backend, but assume parsed based on ChatPage
                  const parsedMeta = typeof metadata === 'string' ? JSON.parse(metadata) : metadata;
                  
                  if (parsedMeta.confidence != null) {
                    confidence = parsedMeta.confidence;
                    confidenceSum += confidence;
                    confidenceCount++;
                  }
                  
                  if (Array.isArray(parsedMeta.sources)) {
                    sourcesCount = parsedMeta.sources.length;
                    hasSources = true;
                  }
                }
              }

              if (hasSources) {
                sourcesSum += sourcesCount;
                validSourcesQueries++;
              }

              feed.push({
                conversationId: detail.conversation_id,
                queryText: msg.content,
                timestamp: msg.created_at,
                botResponsePreview: botResponseText,
                confidence: confidence,
                sourcesCount: sourcesCount
              });
            }
          }
        }

        // Sort feed by timestamp descending
        feed.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        if (isMounted) {
          setStatistics({
            totalConversations: userConversations.length, // total across all time
            totalQueries: totalQueriesCount, // total from top 20
            averageConfidence: confidenceCount > 0 ? (confidenceSum / confidenceCount) : 0,
            averageSources: validSourcesQueries > 0 ? (sourcesSum / validSourcesQueries) : 0,
          });
          setHistoryFeed(feed);
          setIsLoading(false);
        }

      } catch (err) {
        console.error('Failed to load history:', err);
        if (isMounted) {
          setError('Unable to load history and statistics.');
          setIsLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      isMounted = false;
    };
  }, []);

  // Derived Chart Data
  const { activityData, conversationData, confidenceData } = useMemo(() => {
    const activityMap = {};
    const convMap = {};
    let high = 0, med = 0, low = 0;

    historyFeed.forEach(item => {
      // 1. Activity over time
      const dateStr = new Date(item.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      activityMap[dateStr] = (activityMap[dateStr] || 0) + 1;

      // 2. Queries per conversation
      const convIdStr = item.conversationId.substring(0, 6);
      convMap[convIdStr] = (convMap[convIdStr] || 0) + 1;

      // 3. Confidence
      if (item.confidence != null) {
        if (item.confidence > 0.8) high++;
        else if (item.confidence >= 0.5) med++;
        else low++;
      }
    });

    // Reversing keys to show oldest to newest left-to-right (roughly, since feed is descending)
    const activityArr = Object.keys(activityMap).map(date => ({ date, count: activityMap[date] })).reverse();
    
    const convArr = Object.keys(convMap).map(id => ({ id, count: convMap[id] }));

    return {
      activityData: activityArr,
      conversationData: convArr.slice(0, 8), // Limit to top 8 for readability
      confidenceData: { high, med, low, total: high + med + low }
    };
  }, [historyFeed]);

  const maxActivity = Math.max(...activityData.map(d => d.count), 1);
  const maxConv = Math.max(...conversationData.map(d => d.count), 1);

  if (isLoading) {
    return (
      <div className="history-page">
        <div className="history-loading">
          <div className="history-loading-spinner"></div>
          <div>Loading your query history...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-page">
        <div className="history-error">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <h2>Error Loading Data</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }



  return (
    <div className="history-page">
      <header className="history-header">
        <h1>Query History & Statistics</h1>
        <p>Review your recent activity and RAG performance metrics. <br/>
           <small className="history-subtitle">Analytics based on the {statistics.totalConversations > 20 ? "20 most recent" : "recent"} conversations.</small>
        </p>
      </header>

      {/* Stats Grid */}
      <section className="stats-grid">
        <div className="stat-card">
          <span className="stat-title">Total Conversations</span>
          <span className="stat-value">{statistics.totalConversations}</span>
        </div>
        <div className="stat-card">
          <span className="stat-title">Recent Queries</span>
          <span className="stat-value">{statistics.totalQueries}</span>
        </div>
        <div className="stat-card">
          <span className="stat-title">Avg. Confidence</span>
          <span className="stat-value">
            {statistics.averageConfidence > 0 
              ? `${(statistics.averageConfidence * 100).toFixed(1)}%` 
              : 'N/A'}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-title">Avg. Sources / Query</span>
          <span className="stat-value">
            {statistics.averageSources > 0 
              ? statistics.averageSources.toFixed(1)
              : 'N/A'}
          </span>
        </div>
      </section>

      {/* Charts Section */}
      {historyFeed.length > 0 && (
        <section className="charts-container">
          {/* Chart 1: Activity Over Time */}
          <div className="chart-card">
            <h3>Query Activity Over Time</h3>
            {activityData.length > 0 ? (
              <div className="bar-chart-vertical">
                {activityData.map((d, i) => (
                  <div key={i} className="bar-vertical-wrapper" title={`${d.count} queries on ${d.date}`}>
                    <div className="bar-vertical" style={{ height: `${(d.count / maxActivity) * 100}%` }}>
                      <span className="bar-label-top">{d.count}</span>
                    </div>
                    <span className="bar-label-bottom">{d.date}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="chart-empty">No activity data</div>
            )}
          </div>

          {/* Chart 2: Queries Per Conversation */}
          <div className="chart-card">
            <h3>Queries per Conversation</h3>
            {conversationData.length > 0 ? (
              <div className="bar-chart-horizontal">
                {conversationData.map((d, i) => (
                  <div key={i} className="bar-horizontal-row">
                    <span className="bar-horizontal-label">#{d.id}</span>
                    <div className="bar-horizontal-track">
                      <div className="bar-horizontal-fill" style={{ width: `${(d.count / maxConv) * 100}%` }}></div>
                    </div>
                    <span className="bar-horizontal-value">{d.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="chart-empty">No conversation data</div>
            )}
          </div>

          {/* Chart 3: Confidence Distribution */}
          <div className="chart-card">
            <h3>Confidence Distribution</h3>
            {confidenceData.total > 0 ? (
              <div className="confidence-chart">
                <div className="confidence-bar-stacked">
                  <div className="conf-segment conf-high" style={{ width: `${(confidenceData.high / confidenceData.total) * 100}%` }} title={`High: ${confidenceData.high}`}></div>
                  <div className="conf-segment conf-med" style={{ width: `${(confidenceData.med / confidenceData.total) * 100}%` }} title={`Medium: ${confidenceData.med}`}></div>
                  <div className="conf-segment conf-low" style={{ width: `${(confidenceData.low / confidenceData.total) * 100}%` }} title={`Low: ${confidenceData.low}`}></div>
                </div>
                <div className="confidence-legend">
                  <div className="legend-item"><span className="legend-dot conf-high"></span> High ({confidenceData.high})</div>
                  <div className="legend-item"><span className="legend-dot conf-med"></span> Med ({confidenceData.med})</div>
                  <div className="legend-item"><span className="legend-dot conf-low"></span> Low ({confidenceData.low})</div>
                </div>
              </div>
            ) : (
              <div className="chart-empty">No confidence data available</div>
            )}
          </div>
        </section>
      )}

      {/* History Feed */}
      <section className="history-section">
        <h2>Recent Queries</h2>
        
        {historyFeed.length === 0 ? (
          <div className="history-empty">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <p>No queries found. Start a chat to see your history!</p>
          </div>
        ) : (
          <div className="history-feed">
            {historyFeed.map((item, idx) => (
              <div key={idx} className="history-item">
                <div className="history-item-header">
                  <span className="history-timestamp">
                    {new Date(item.timestamp).toLocaleString()}
                  </span>
                  <div className="history-metrics">
                    {item.sourcesCount > 0 && (
                      <span className="metric-badge">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                          <polyline points="14 2 14 8 20 8"></polyline>
                        </svg>
                        {item.sourcesCount} sources
                      </span>
                    )}
                    {item.confidence != null && (
                      <span className={`metric-badge ${item.confidence > 0.8 ? 'confidence-high' : 'confidence-med'}`}>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                        {(item.confidence * 100).toFixed(1)}% confidence
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="history-query">{item.queryText}</div>
                
                <div className="history-response">
                  {item.botResponsePreview.length > 200 
                    ? item.botResponsePreview.substring(0, 200) + '...' 
                    : item.botResponsePreview}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
