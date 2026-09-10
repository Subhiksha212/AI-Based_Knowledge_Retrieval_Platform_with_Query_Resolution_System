"""
Conversation memory storage helpers.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.core.models import Conversation, ConversationMessage
from .schemas import ConversationTurn


def _safe_json_dumps(value: Any) -> str | None:
    """
    Serialize metadata safely.

    Returns None when there is nothing to store.
    """
    if value is None:
        return None

    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )
    except (TypeError, ValueError):
        return None


def _safe_json_loads(value: str | None) -> dict:
    """
    Deserialize stored metadata safely.
    """
    if not value:
        return {}

    try:
        result = json.loads(value)

        if isinstance(result, dict):
            return result

        return {}

    except (TypeError, ValueError, json.JSONDecodeError):
        return {}


def save_turn(
    db: Session,
    turn: ConversationTurn,
    response_metadata: dict | None = None,
):
    """
    Save one user/assistant turn.

    response_metadata is attached only to the assistant message.
    """

    conversation = db.get(
        Conversation,
        turn.conversation_id,
    )

    if conversation is None:
        raise ValueError(
            "Conversation does not exist."
        )

    # ---------------------------------------------------------------
    # User message
    # ---------------------------------------------------------------

    user_message = ConversationMessage(
        conversation_id=turn.conversation_id,
        role="user",
        content=turn.user_query,
    )

    db.add(user_message)

    # ---------------------------------------------------------------
    # Assistant message
    # ---------------------------------------------------------------

    if turn.ai_response:
        assistant_message = ConversationMessage(
            conversation_id=turn.conversation_id,
            role="assistant",
            content=turn.ai_response,
            message_metadata=_safe_json_dumps(
                response_metadata
            ),
        )

        db.add(assistant_message)

    # ---------------------------------------------------------------
    # Force conversation timestamp update.
    #
    # This ensures updated_at changes whenever a message
    # is added, so the latest active conversation remains first.
    # ---------------------------------------------------------------

    conversation.updated_at = db.execute(
        Conversation.__table__.select()
        .with_only_columns(
            Conversation.updated_at
        )
        .where(
            Conversation.id == turn.conversation_id
        )
    ).scalar_one_or_none() or conversation.updated_at

    db.commit()


def get_history(
    db: Session,
    conversation_id: str,
):
    """
    Return all messages for a conversation.
    """

    messages = (
        db.query(ConversationMessage)
        .filter(
            ConversationMessage.conversation_id
            == conversation_id
        )
        .order_by(
            ConversationMessage.created_at.asc()
        )
        .all()
    )

    return messages


def get_message_metadata(
    message: ConversationMessage,
) -> dict:
    """
    Return decoded message metadata.
    """

    return _safe_json_loads(
        message.message_metadata
    )