"""
FastAPI routes for Query Analytics.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.analytics.schemas import (
    AnalyticsOverview,
    QueryAnalyticsCreate,
    QueryAnalyticsResponse,
)
from app.analytics.service import (
    get_overview,
    get_query_type_statistics,
    log_query,
)
from app.core.database import get_db


router = APIRouter(
    prefix="/analytics",
    tags=["Query Analytics"],
)


@router.post(
    "/log",
    response_model=QueryAnalyticsResponse,
    summary="Log Query Analytics",
)
def create_query_analytics(
    data: QueryAnalyticsCreate,
    db: Session = Depends(get_db),
):
    """
    Store analytics information for a query.
    """

    return log_query(
        db=db,
        data=data,
    )


@router.get(
    "/overview",
    response_model=AnalyticsOverview,
    summary="Get Analytics Overview",
)
def analytics_overview(
    db: Session = Depends(get_db),
):
    """
    Return overall query statistics.
    """

    return get_overview(db)


@router.get(
    "/query-types",
    summary="Get Query Type Statistics",
)
def query_type_statistics(
    db: Session = Depends(get_db),
):
    """
    Return query counts grouped by query type.
    """

    return get_query_type_statistics(db)