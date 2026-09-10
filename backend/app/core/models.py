"""
SQLAlchemy database models for QueryNest.

Models:
- User
- Conversation
- ConversationMessage
- KnowledgeBaseDocument
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """
    Represents an authenticated QueryNest user.
    """

    __tablename__ = "users"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    full_name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash = Column(
        String(255),
        nullable=False,
    )

    role = Column(
        String(50),
        nullable=False,
        default="User",
    )

    avatar = Column(
        String(500),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # User-specific knowledge base documents
    knowledge_base_documents = relationship(
        "KnowledgeBaseDocument",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Conversation(Base):
    """
    Represents one user's persistent conversation.
    """

    __tablename__ = "conversations"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id = Column(
        String(36),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="conversations",
    )

    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class ConversationMessage(Base):
    """
    Represents a single user or assistant message.

    message_metadata stores optional JSON-encoded information
    associated with the message, such as:
    - sources
    - retrieval results
    - confidence
    - speech text
    """

    __tablename__ = "conversation_messages"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    conversation_id = Column(
        String(36),
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    role = Column(
        String(20),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    message_metadata = Column(
        "message_metadata",
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages",
    )


class KnowledgeBaseDocument(Base):
    """
    Represents a document uploaded by a specific user
    to their personal knowledge base.
    """

    __tablename__ = "knowledge_base_documents"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id = Column(
        String(36),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    filename = Column(
        String(255),
        nullable=False,
    )

    original_filename = Column(
        String(255),
        nullable=True,
    )

    file_type = Column(
        String(50),
        nullable=True,
    )

    file_size = Column(
        Integer,
        nullable=True,
    )

    status = Column(
        String(50),
        nullable=False,
        default="processing",
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="knowledge_base_documents",
    )