"""add user_id to knowledge_gaps

Revision ID: e9b7e767c397
Revises: 5a7a6c2b7c8f
Create Date: 2026-09-12 15:22:00.152781
"""

from typing import Sequence, Union

from alembic import op


revision: str = "e9b7e767c397"
down_revision: Union[str, Sequence[str], None] = "5a7a6c2b7c8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_foreign_key(
        "fk_knowledge_gaps_user_id_users",
        "knowledge_gaps",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_knowledge_gaps_user_id_users",
        "knowledge_gaps",
        type_="foreignkey",
    )