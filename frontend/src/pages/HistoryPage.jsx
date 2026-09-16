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

        const userConversations = Array.isArray(
          convData?.conversations
        )
          ? convData.conversations
          : [];

        if (!isMounted) {
          return;
        }

        if (userConversations.length === 0) {
          setStatistics({
            totalConversations: 0,
            totalQueries: 0,
            averageConfidence: 0,
            averageSources: 0,
          });

          setHistoryFeed([]);
          setIsLoading(false);
          return;
        }

        // 2. Limit detailed fetching to the 20 most recent conversations.
        // The backend sorts by updated_at descending.
        const topConversations = userConversations.slice(0, 20);

        // 3. Fetch detailed messages for these conversations in parallel.
        const detailsPromises = topConversations.map((conv) =>
          api
            .getConversation(conv.conversation_id)
            .catch((err) => {
              console.warn(
                `Failed to fetch details for ${conv.conversation_id}`,
                err
              );
              return null;
            })
        );

        const detailedConversations =
          await Promise.all(detailsPromises);

        if (!isMounted) {
          return;
        }

        // 4. Calculate stats and build the feed
        let totalQueriesCount = 0;
        let confidenceSum = 0;
        let confidenceCount = 0;
        let sourcesSum = 0;
        let validSourcesQueries = 0;

        const feed = [];

        for (const detail of detailedConversations) {
          if (
            !detail ||
            !Array.isArray(detail.messages)
          ) {
            continue;
          }

          // Process messages for stats and feed mapping
          for (
            let i = 0;
            i < detail.messages.length;
            i++
          ) {
            const msg = detail.messages[i];

            if (msg.role === 'user') {
              totalQueriesCount++;

              // Find the immediate next bot response
              const nextMsg = detail.messages[i + 1];

              let confidence = null;
              let sourcesCount = 0;
              let hasSources = false;
              let botResponseText = 'No response';

              if (
                nextMsg &&
                nextMsg.role !== 'user'
              ) {
                botResponseText =
                  nextMsg.content || 'No response';

                const metadata =
                  nextMsg.message_metadata;

                if (metadata) {
                  try {
                    // Some metadata might be stringified
                    // depending on the backend.
                    const parsedMeta =
                      typeof metadata === 'string'
                        ? JSON.parse(metadata)
                        : metadata;

                    // Refusal answers are unanswered retrieval queries.
                    // Older persisted messages may still contain the original
                    // retrieval confidence, so derive the unanswered state
                    // from the response text for this frontend-only history
                    // page.
                    const normalizedResponse =
                      String(botResponseText || '')
                        .trim()
                        .toLowerCase();

                    const refusalPatterns = [
                      'the retrieved documents do not contain',
                      'retrieved documents do not contain',
                      'the retrieved context does not contain',
                      'retrieved context does not contain',
                      'i don\'t have enough information',
                      'i do not have enough information',
                      'no information is available',
                      'no information is provided',
                      'the available context does not contain',
                      'the available context does not provide',
                      'the context does not contain',
                      'cannot answer from the available context',
                      "can't answer from the available context",
                      'not enough information in the available knowledge base',
                    ];

                    const isUnanswered =
                      refusalPatterns.some((pattern) =>
                        normalizedResponse.includes(pattern)
                      );

                    if (isUnanswered) {
                      // Display unanswered retrieval responses as 0% and do
                      // not include them in the average confidence.
                      confidence = 0;
                    } else if (
                      parsedMeta.confidence != null
                    ) {
                      confidence =
                        Number(parsedMeta.confidence);

                      if (Number.isFinite(confidence)) {
                        confidenceSum += confidence;
                        confidenceCount++;
                      } else {
                        confidence = null;
                      }
                    }

                    if (
                      Array.isArray(
                        parsedMeta.sources
                      )
                    ) {
                      sourcesCount =
                        parsedMeta.sources.length;
                      hasSources = true;
                    }
                  } catch (metadataError) {
                    console.warn(
                      'Failed to parse message metadata:',
                      metadataError
                    );
                  }
                }
              }

              if (hasSources) {
                sourcesSum += sourcesCount;
                validSourcesQueries++;
              }

              feed.push({
                conversationId:
                  detail.conversation_id,
                queryText: msg.content,
                timestamp: msg.created_at,
                botResponsePreview:
                  botResponseText,
                confidence: confidence,
                sourcesCount: sourcesCount,
              });
            }
          }
        }

        // Sort feed by timestamp descending
        feed.sort(
          (a, b) =>
            new Date(b.timestamp) -
            new Date(a.timestamp)
        );

        if (isMounted) {
          setStatistics({
            // Total across all conversations
            totalConversations:
              userConversations.length,

            // Total queries from the recent conversations
            totalQueries: totalQueriesCount,

            averageConfidence:
              confidenceCount > 0
                ? confidenceSum / confidenceCount
                : 0,

            averageSources:
              validSourcesQueries > 0
                ? sourcesSum / validSourcesQueries
                : 0,
          });

          setHistoryFeed(feed);
          setIsLoading(false);
        }
      } catch (err) {
        console.error(
          'Failed to load history:',
          err
        );

        if (isMounted) {
          setError(
            'Unable to load history and statistics.'
          );
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
  const {
    activityData,
    conversationData,
    confidenceData,
  } = useMemo(() => {
    const activityMap = {};
    const convMap = {};

    let high = 0;
    let med = 0;
    let low = 0;

    historyFeed.forEach((item) => {
      // 1. Activity over time
      const dateStr = new Date(
        item.timestamp
      ).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
      });

      activityMap[dateStr] =
        (activityMap[dateStr] || 0) + 1;

      // 2. Queries per conversation
      const convIdStr =
        item.conversationId.substring(0, 6);

      convMap[convIdStr] =
        (convMap[convIdStr] || 0) + 1;

      // 3. Confidence
      if (item.confidence != null) {
        if (item.confidence > 0.8) {
          high++;
        } else if (item.confidence >= 0.5) {
          med++;
        } else {
          low++;
        }
      }
    });

    // Reverse keys to show oldest to newest
    // left-to-right approximately.
    const activityArr = Object.keys(activityMap)
      .map((date) => ({
        date,
        count: activityMap[date],
      }))
      .reverse();

    const convArr = Object.keys(convMap).map(
      (id) => ({
        id,
        count: convMap[id],
      })
    );

    return {
      activityData: activityArr,
      conversationData: convArr.slice(0, 8),
      confidenceData: {
        high,
        med,
        low,
        total: high + med + low,
      },
    };
  }, [historyFeed]);

  const maxActivity = Math.max(
    ...activityData.map((d) => d.count),
    1
  );

  const maxConv = Math.max(
    ...conversationData.map((d) => d.count),
    1
  );

  if (isLoading) {
    return (
      <div className="history-page">
        <div className="history-loading">
          <div className="history-loading-spinner"></div>
          <div>
            Loading your query history...
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-page">
        <div className="history-error">
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <circle
              cx="12"
              cy="12"
              r="10"
            ></circle>
            <line
              x1="12"
              y1="8"
              x2="12"
              y2="12"
            ></line>
            <line
              x1="12"
              y1="16"
              x2="12.01"
              y2="16"
            ></line>
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
        <h1>Query History &amp; Statistics</h1>

        <p>
          Review your recent activity and Statistics
          <br />

          <small className="history-subtitle">
            Analytics based on the{' '}
            {statistics.totalConversations > 20
              ? '20 most recent'
              : 'recent'}{' '}
            conversations
          </small>
        </p>
      </header>

      {/* Stats Grid */}
      <section className="stats-grid">
        <div className="stat-card">
          <span className="stat-title">
            Total Conversations
          </span>

          <span className="stat-value">
            {statistics.totalConversations}
          </span>
        </div>

        <div className="stat-card">
          <span className="stat-title">
            Recent Queries
          </span>

          <span className="stat-value">
            {statistics.totalQueries}
          </span>
        </div>

      </section>

      {/* Charts Section */}
      {historyFeed.length > 0 && (
        <section className="charts-container">
          {/* Chart 1: Activity Over Time */}
          <div className="chart-card">
            <h3>
              Query Activity Over Time
            </h3>

            {activityData.length > 0 ? (
              <div className="bar-chart-vertical">
                {activityData.map((d, i) => (
                  <div
                    key={i}
                    className="bar-vertical-wrapper"
                    title={`${d.count} queries on ${d.date}`}
                  >
                    <div
                      className="bar-vertical"
                      style={{
                        height: `${
                          (d.count / maxActivity) *
                          100
                        }%`,
                      }}
                    >
                      <span className="bar-label-top">
                        {d.count}
                      </span>
                    </div>

                    <span className="bar-label-bottom">
                      {d.date}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="chart-empty">
                No activity data
              </div>
            )}
          </div>

          {/* Chart 2: Queries Per Conversation */}
          <div className="chart-card">
            <h3>
              Queries per Conversation
            </h3>

            {conversationData.length > 0 ? (
              <div className="bar-chart-horizontal">
                {conversationData.map((d, i) => (
                  <div
                    key={i}
                    className="bar-horizontal-row"
                  >
                    <span className="bar-horizontal-label">
                      #{d.id}
                    </span>

                    <div className="bar-horizontal-track">
                      <div
                        className="bar-horizontal-fill"
                        style={{
                          width: `${
                            (d.count / maxConv) *
                            100
                          }%`,
                        }}
                      ></div>
                    </div>

                    <span className="bar-horizontal-value">
                      {d.count}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="chart-empty">
                No conversation data
              </div>
            )}
          </div>

        </section>
      )}

      {/* History Feed */}
      <section className="history-section">
        <h2>Recent Queries</h2>

        {historyFeed.length === 0 ? (
          <div className="history-empty">
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>

            <p>
              No queries found. Start a chat to
              see your history!
            </p>
          </div>
        ) : (
          <div className="history-feed">
            {historyFeed.map(
              (item, idx) => (
                <div
                  key={idx}
                  className="history-item"
                >
                  <div className="history-item-header">
                    <span className="history-timestamp">
                      {new Date(
                        item.timestamp
                      ).toLocaleString()}
                    </span>

                    <div className="history-metrics">
                      {item.sourcesCount > 0 && (
                        <span className="metric-badge">
                          <svg
                            width="12"
                            height="12"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                          >
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                          </svg>

                          {item.sourcesCount} sources
                        </span>
                      )}

                      {item.confidence != null && (
                        <span
                          className={`metric-badge ${
                            item.confidence > 0.8
                              ? 'confidence-high'
                              : 'confidence-med'
                          }`}
                        >
                          <svg
                            width="12"
                            height="12"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                          >
                            <polyline points="20 6 9 17 4 12"></polyline>
                          </svg>

                          {(
                            item.confidence * 100
                          ).toFixed(1)}
                          % confidence
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="history-query">
                    {item.queryText}
                  </div>

                  <div className="history-response">
                    {item.botResponsePreview.length >
                    200
                      ? item.botResponsePreview.substring(
                          0,
                          200
                        ) + '...'
                      : item.botResponsePreview}
                  </div>
                </div>
              )
            )}
          </div>
        )}
      </section>
    </div>
  );
}