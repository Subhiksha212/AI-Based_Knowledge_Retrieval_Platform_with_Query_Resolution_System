"""
Business logic for Query Analytics.
"""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.analytics.models import QueryAnalytics
from app.analytics.schemas import (
    AnalyticsOverview,
    QueryAnalyticsCreate,
)


def log_query(
    db: Session,
    data: QueryAnalyticsCreate,
) -> QueryAnalytics:
    """
    Store analytics information for a query.
    """

    analytics = QueryAnalytics(
        user_id=data.user_id,
        conversation_id=data.conversation_id,
        query_text=data.query_text,
        query_type=data.query_type,
        response_status=data.response_status,
        confidence_score=data.confidence_score,
        response_time=data.response_time,
    )

    db.add(analytics)
    db.commit()
    db.refresh(analytics)

    return analytics


def get_total_queries(
    db: Session,
) -> int:
    """
    Return total number of queries.
    """

    return (
        db.query(QueryAnalytics)
        .count()
    )


def get_answered_queries(
    db: Session,
) -> int:
    """
    Return number of answered queries.
    """

    return (
        db.query(QueryAnalytics)
        .filter(
            QueryAnalytics.response_status
            == "answered"
        )
        .count()
    )


def get_unanswered_queries(
    db: Session,
) -> int:
    """
    Return number of unanswered queries.
    """

    return (
        db.query(QueryAnalytics)
        .filter(
            QueryAnalytics.response_status
            == "unanswered"
        )
        .count()
    )


def get_average_confidence(
    db: Session,
) -> float | None:
    """
    Calculate average confidence score.
    """

    result = (
        db.query(
            func.avg(
                QueryAnalytics.confidence_score
            )
        )
        .scalar()
    )

    if result is None:
        return None

    return round(float(result), 3)


def get_average_response_time(
    db: Session,
) -> float | None:
    """
    Calculate average response time in seconds.
    """

    result = (
        db.query(
            func.avg(
                QueryAnalytics.response_time
            )
        )
        .scalar()
    )

    if result is None:
        return None

    return round(float(result), 3)


def get_overview(
    db: Session,
) -> AnalyticsOverview:
    """
    Return overall query analytics.
    """

    total = get_total_queries(db)

    answered = get_answered_queries(db)

    unanswered = get_unanswered_queries(db)

    average_confidence = (
        get_average_confidence(db)
    )

    average_response_time = (
        get_average_response_time(db)
    )

    return AnalyticsOverview(
        total_queries=total,
        answered_queries=answered,
        unanswered_queries=unanswered,
        average_confidence=average_confidence,
        average_response_time=average_response_time,
    )


def get_query_type_statistics(
    db: Session,
) -> list[dict]:
    """
    Return number of queries grouped by query type.
    """

    results = (
        db.query(
            QueryAnalytics.query_type,
            func.count(QueryAnalytics.id),
        )
        .filter(
            QueryAnalytics.query_type.isnot(None)
        )
        .group_by(
            QueryAnalytics.query_type
        )
        .all()
    )

    return [
        {
            "query_type": query_type,
            "count": count,
        }
        for query_type, count in results
    ]