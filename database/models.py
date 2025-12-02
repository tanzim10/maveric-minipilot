"""
SQLAlchemy models for Maveric MiniPilot chatbot.

This module defines the database schema:
- User: User accounts and sessions
- Conversation: Chat conversations
- Message: Individual messages in conversations
- KnowledgeChunk: Chunks from knowledge base (enhanced README, docs, etc.)
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, 
    Enum, JSON, Index, func
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database.db_config import Base


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps."""
    created_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Timestamp when record was created"
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when record was last updated"
    )


class User(Base, TimestampMixin):
    """
    User model representing chatbot users.
    
    Supports both authenticated users (with email) and anonymous/guest users.
    """
    __tablename__ = "users"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique user identifier (UUID)"
    )
    
    external_id = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="External user ID from authentication system (optional)"
    )
    
    name = Column(
        String(255),
        nullable=True,
        comment="User's display name"
    )
    
    email = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="User's email address (unique, nullable for guest users)"
    )
    
    # Relationships
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"


class Conversation(Base, TimestampMixin):
    """
    Conversation model representing a chat session.
    
    A conversation belongs to a user (or can be anonymous) and contains
    multiple messages. Conversations can be active or archived.
    """
    __tablename__ = "conversations"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique conversation identifier (UUID)"
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="User who owns this conversation (nullable for anonymous)"
    )
    
    title = Column(
        String(500),
        nullable=True,
        comment="Conversation title (auto-generated or user-provided)"
    )
    
    status = Column(
        String(50),
        default="active",
        nullable=False,
        index=True,
        comment="Conversation status: 'active' or 'archived'"
    )
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
        lazy="dynamic"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_conversation_user_status", "user_id", "status"),
        Index("idx_conversation_created", "created_at"),
    )
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, status={self.status})>"


class MessageSenderType:
    """Enum-like class for message sender types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base, TimestampMixin):
    """
    Message model representing individual messages in a conversation.
    
    Messages can be from:
    - user: User input/query
    - assistant: Bot response
    - system: System messages (errors, info, etc.)
    
    The role_metadata field can store additional information like:
    - Tool calls made by assistant
    - Retrieved knowledge chunks
    - Token counts
    - Model used
    """
    __tablename__ = "messages"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique message identifier (UUID)"
    )
    
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Conversation this message belongs to"
    )
    
    sender_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of sender: 'user', 'assistant', or 'system'"
    )
    
    content = Column(
        Text,
        nullable=False,
        comment="Message content/text"
    )
    
    role_metadata = Column(
        JSON,
        nullable=True,
        comment="Additional metadata (tool calls, retrieved chunks, token counts, etc.)"
    )
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_message_conversation_created", "conversation_id", "created_at"),
        Index("idx_message_sender_type", "sender_type"),
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, sender_type={self.sender_type})>"


class KnowledgeChunk(Base, TimestampMixin):
    """
    KnowledgeChunk model representing chunks from the knowledge base.
    
    These chunks come from:
    - Enhanced README (from readme_generator)
    - Documentation files
    - Module-specific guides
    
    The actual embeddings are stored in the vector database (ChromaDB/FAISS),
    but this table stores the metadata and content for reference.
    """
    __tablename__ = "knowledge_chunks"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique knowledge chunk identifier (UUID)"
    )
    
    source = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Source of the chunk (e.g., 'enhanced_readme', 'docs', module name)"
    )
    
    external_id = Column(
        String(500),
        nullable=True,
        index=True,
        comment="External identifier (e.g., file path + chunk index, section ID)"
    )
    
    title = Column(
        String(500),
        nullable=True,
        comment="Chunk title or heading"
    )
    
    content = Column(
        Text,
        nullable=False,
        comment="Chunk content/text"
    )
    
    chunk_metadata = Column(
        JSON,
        nullable=True,
        comment="Additional metadata (section_type, module, line_numbers, etc.)"
    )
    
    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_knowledge_source", "source"),
        Index("idx_knowledge_external_id", "external_id"),
        Index("idx_knowledge_created", "created_at"),
    )
    
    def __repr__(self):
        return f"<KnowledgeChunk(id={self.id}, source={self.source}, title={self.title})>"

