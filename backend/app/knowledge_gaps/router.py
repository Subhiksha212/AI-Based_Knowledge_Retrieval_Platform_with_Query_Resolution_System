from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.knowledge_gaps.schemas import KnowledgeGapResponse, KnowledgeGapStatistics
from app.knowledge_gaps.service import (
    get_gap_statistics,
    get_knowledge_gaps,
    get_top_knowledge_gaps,
)


router = APIRouter(
    prefix="/knowledge-gaps",
    tags=["Knowledge Gap Detection"],
)


@router.get("", response_model=list[KnowledgeGapResponse])
def list_knowledge_gaps(db: Session = Depends(get_db)):
    return get_knowledge_gaps(db)


@router.get("/top", response_model=list[KnowledgeGapResponse])
def top_knowledge_gaps(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_top_knowledge_gaps(db=db, limit=limit)


@router.get("/statistics", response_model=KnowledgeGapStatistics)
def knowledge_gap_statistics(db: Session = Depends(get_db)):
    return get_gap_statistics(db)
