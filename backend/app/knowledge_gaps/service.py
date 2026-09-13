from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.knowledge_gaps.models import KnowledgeGap
from app.knowledge_gaps.schemas import KnowledgeGapCreate, KnowledgeGapStatistics


CONFIDENCE_THRESHOLD = 0.50


def detect_knowledge_gap(
    response_status: str,
    confidence_score: float | None,
    retrieval_count: int,
) -> tuple[bool, str | None]:
    """Return whether the query indicates a knowledge gap."""

    if response_status == "unanswered":
        return True, "Unanswered query"

    if retrieval_count == 0:
        return True, "No relevant chunks"

    if confidence_score is not None and confidence_score < CONFIDENCE_THRESHOLD:
        return True, "Low confidence"

    return False, None


def create_knowledge_gap(
    db: Session,
    data: KnowledgeGapCreate,
) -> KnowledgeGap:
    """Create a gap or increment the count for an exact repeated query."""

    existing_gap = (
        db.query(KnowledgeGap)
        .filter(
            func.lower(KnowledgeGap.query_text)
            == data.query_text.lower()
        )
        .first()
    )

    if existing_gap:
        existing_gap.occurrence_count += 1

        if data.confidence_score is not None:
            existing_gap.confidence_score = data.confidence_score

        db.commit()
        db.refresh(existing_gap)
        return existing_gap

    gap = KnowledgeGap(
        query_text=data.query_text,
        query_type=data.query_type,
        reason=data.reason,
        confidence_score=data.confidence_score,
        occurrence_count=1,
        status="open",
    )

    db.add(gap)
    db.commit()
    db.refresh(gap)
    return gap


def get_knowledge_gaps(db: Session) -> list[KnowledgeGap]:
    return (
        db.query(KnowledgeGap)
        .order_by(KnowledgeGap.occurrence_count.desc())
        .all()
    )


def get_top_knowledge_gaps(
    db: Session,
    limit: int = 10,
) -> list[KnowledgeGap]:
    return (
        db.query(KnowledgeGap)
        .order_by(KnowledgeGap.occurrence_count.desc())
        .limit(limit)
        .all()
    )


def get_gap_statistics(db: Session) -> KnowledgeGapStatistics:
    total = db.query(KnowledgeGap).count()

    open_gaps = (
        db.query(KnowledgeGap)
        .filter(KnowledgeGap.status == "open")
        .count()
    )

    resolved_gaps = (
        db.query(KnowledgeGap)
        .filter(KnowledgeGap.status == "resolved")
        .count()
    )

    reason_result = (
        db.query(KnowledgeGap.reason, func.count(KnowledgeGap.id))
        .group_by(KnowledgeGap.reason)
        .order_by(func.count(KnowledgeGap.id).desc())
        .first()
    )

    return KnowledgeGapStatistics(
        total_gaps=total,
        open_gaps=open_gaps,
        resolved_gaps=resolved_gaps,
        most_common_reason=reason_result[0] if reason_result else None,
    )
