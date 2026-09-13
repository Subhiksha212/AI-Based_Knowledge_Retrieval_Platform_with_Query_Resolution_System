Milestone 4 - Knowledge Gap Detection

Place this folder at:
backend/app/knowledge_gaps/

Files:
__init__.py
models.py
schemas.py
service.py
router.py

Detection:
- unanswered response
- zero retrieval chunks
- confidence below 0.50

APIs:
GET /knowledge-gaps
GET /knowledge-gaps/top
GET /knowledge-gaps/statistics

Register in the FastAPI main app:
from app.knowledge_gaps.router import router as knowledge_gap_router
app.include_router(knowledge_gap_router)

The detector must also be called from the existing query workflow using
the project's actual state field names.
