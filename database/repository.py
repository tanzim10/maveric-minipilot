"""
Repository layer for database operations.

This module provides high-level CRUD and query functions for all models.
All functions accept a session parameter to allow transaction management
at the service layer.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from database.models import (
    User, Conversation, Message, KnowledgeChunk,
    MessageSenderType
)


# ============================================================================
# User Repository Functions
# ============================================================================

def create_user(
    session: Session,
    email: Optional[str] = None,
    name: Optional[str] = None,
    external_id: Optional[str] = None
) -> User:
    """
    Create a new user.
    
    Args:
        session: Database session
        email: User email (optional)
        name: User name (optional)
        external_id: External user ID from auth system (optional)
    
    Returns:
        Created User object
    
    Raises:
        IntegrityError: If email or external_id already exists
    """
    user = User(
        email=email,
        name=name,
        external_id=external_id
    )
    session.add(user)
    session.flush()  # Get the ID without committing
    return user


def get_user_by_id(session: Session, user_id: UUID) -> Optional[User]:
    """
    Get user by ID.
    
    Args:
        session: Database session
        user_id: User UUID
    
    Returns:
        User object or None if not found
    """
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """
    Get user by email.
    
    Args:
        session: Database session
        email: User email
    
    Returns:
        User object or None if not found
    """
    return session.query(User).filter(User.email == email).first()


def get_user_by_external_id(session: Session, external_id: str) -> Optional[User]:
    """
    Get user by external ID.
    
    Args:
        session: Database session
        external_id: External user ID from auth system
    
    Returns:
        User object or None if not found
    """
    return session.query(User).filter(User.external_id == external_id).first()


def get_or_create_user_by_external_id(
    session: Session,
    external_id: str,
    email: Optional[str] = None,
    name: Optional[str] = None
) -> tuple[User, bool]:
    """
    Get existing user by external_id or create new one.
    
    Args:
        session: Database session
        external_id: External user ID from auth system
        email: User email (used if creating new user)
        name: User name (used if creating new user)
    
    Returns:
        Tuple of (User object, created: bool)
    """
    user = get_user_by_external_id(session, external_id)
    if user:
        return user, False
    
    user = create_user(session, email=email, name=name, external_id=external_id)
    return user, True


def list_users(session: Session, limit: int = 100, offset: int = 0) -> List[User]:
    """
    List all users with pagination.
    
    Args:
        session: Database session
        limit: Maximum number of users to return
        offset: Number of users to skip
    
    Returns:
        List of User objects
    """
    return session.query(User).offset(offset).limit(limit).all()


def update_user(
    session: Session,
    user_id: UUID,
    email: Optional[str] = None,
    name: Optional[str] = None
) -> Optional[User]:
    """
    Update user information.
    
    Args:
        session: Database session
        user_id: User UUID
        email: New email (optional)
        name: New name (optional)
    
    Returns:
        Updated User object or None if not found
    """
    user = get_user_by_id(session, user_id)
    if not user:
        return None
    
    if email is not None:
        user.email = email
    if name is not None:
        user.name = name
    
    session.flush()
    return user


def delete_user(session: Session, user_id: UUID) -> bool:
    """
    Delete a user and all associated conversations.
    
    Args:
        session: Database session
        user_id: User UUID
    
    Returns:
        True if user was deleted, False if not found
    """
    user = get_user_by_id(session, user_id)
    if not user:
        return False
    
    session.delete(user)
    session.flush()
    return True


# ============================================================================
# Conversation Repository Functions
# ============================================================================

def create_conversation(
    session: Session,
    user_id: Optional[UUID] = None,
    title: Optional[str] = None,
    status: str = "active"
) -> Conversation:
    """
    Create a new conversation.
    
    Args:
        session: Database session
        user_id: User UUID (optional for anonymous conversations)
        title: Conversation title (optional)
        status: Conversation status (default: "active")
    
    Returns:
        Created Conversation object
    """
    conversation = Conversation(
        user_id=user_id,
        title=title,
        status=status
    )
    session.add(conversation)
    session.flush()
    return conversation


def get_conversation_by_id(session: Session, conversation_id: UUID) -> Optional[Conversation]:
    """
    Get conversation by ID.
    
    Args:
        session: Database session
        conversation_id: Conversation UUID
    
    Returns:
        Conversation object or None if not found
    """
    return session.query(Conversation).filter(Conversation.id == conversation_id).first()


def list_conversations_for_user(
    session: Session,
    user_id: UUID,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Conversation]:
    """
    List conversations for a user with optional status filter.
    
    Args:
        session: Database session
        user_id: User UUID
        status: Filter by status (optional)
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip
    
    Returns:
        List of Conversation objects
    """
    query = session.query(Conversation).filter(Conversation.user_id == user_id)
    
    if status:
        query = query.filter(Conversation.status == status)
    
    return query.order_by(desc(Conversation.created_at)).offset(offset).limit(limit).all()


def list_all_conversations(
    session: Session,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Conversation]:
    """
    List all conversations with optional status filter.
    
    Args:
        session: Database session
        status: Filter by status (optional)
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip
    
    Returns:
        List of Conversation objects
    """
    query = session.query(Conversation)
    
    if status:
        query = query.filter(Conversation.status == status)
    
    return query.order_by(desc(Conversation.created_at)).offset(offset).limit(limit).all()


def update_conversation(
    session: Session,
    conversation_id: UUID,
    title: Optional[str] = None,
    status: Optional[str] = None
) -> Optional[Conversation]:
    """
    Update conversation information.
    
    Args:
        session: Database session
        conversation_id: Conversation UUID
        title: New title (optional)
        status: New status (optional)
    
    Returns:
        Updated Conversation object or None if not found
    """
    conversation = get_conversation_by_id(session, conversation_id)
    if not conversation:
        return None
    
    if title is not None:
        conversation.title = title
    if status is not None:
        conversation.status = status
    
    session.flush()
    return conversation


def archive_conversation(session: Session, conversation_id: UUID) -> Optional[Conversation]:
    """
    Archive a conversation (set status to "archived").
    
    Args:
        session: Database session
        conversation_id: Conversation UUID
    
    Returns:
        Updated Conversation object or None if not found
    """
    return update_conversation(session, conversation_id, status="archived")


def delete_conversation(session: Session, conversation_id: UUID) -> bool:
    """
    Delete a conversation and all associated messages.
    
    Args:
        session: Database session
        conversation_id: Conversation UUID
    
    Returns:
        True if conversation was deleted, False if not found
    """
    conversation = get_conversation_by_id(session, conversation_id)
    if not conversation:
        return False
    
    session.delete(conversation)
    session.flush()
    return True


# ============================================================================
# Message Repository Functions
# ============================================================================

def add_message(
    session: Session,
    conversation_id: UUID,
    sender_type: str,
    content: str,
    role_metadata: Optional[Dict[str, Any]] = None
) -> Message:
    """
    Add a message to a conversation.
    
    Args:
        session: Database session
        conversation_id: Conversation UUID
        sender_type: Type of sender ("user", "assistant", or "system")
        content: Message content
        role_metadata: Additional metadata (optional)
    
    Returns:
        Created Message object
    
    Raises:
        IntegrityError: If conversation_id doesn't exist
    """
    message = Message(
        conversation_id=conversation_id,
        sender_type=sender_type,
        content=content,
        role_metadata=role_metadata
    )
    session.add(message)
    session.flush()
    return message


def get_message_by_id(session: Session, message_id: UUID) -> Optional[Message]:
    """
    Get message by ID.
    
    Args:
        session: Database session
        message_id: Message UUID
    
    Returns:
        Message object or None if not found
    """
    return session.query(Message).filter(Message.id == message_id).first()


def list_messages_for_conversation(
    session: Session,
    conversation_id: UUID,
    limit: int = 100,
    offset: int = 0,
    sender_type: Optional[str] = None
) -> List[Message]:
    """
    List messages for a conversation with pagination.
    
    Args:
        session: Database session
        conversation_id: Conversation UUID
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        sender_type: Filter by sender type (optional)
    
    Returns:
        List of Message objects ordered by created_at
    """
    query = session.query(Message).filter(Message.conversation_id == conversation_id)
    
    if sender_type:
        query = query.filter(Message.sender_type == sender_type)
    
    return query.order_by(Message.created_at).offset(offset).limit(limit).all()


def get_conversation_message_count(session: Session, conversation_id: UUID) -> int:
    """
    Get total message count for a conversation.
    
    Args:
        session: Database session
        conversation_id: Conversation UUID
    
    Returns:
        Total number of messages
    """
    return session.query(Message).filter(Message.conversation_id == conversation_id).count()


def delete_message(session: Session, message_id: UUID) -> bool:
    """
    Delete a message.
    
    Args:
        session: Database session
        message_id: Message UUID
    
    Returns:
        True if message was deleted, False if not found
    """
    message = get_message_by_id(session, message_id)
    if not message:
        return False
    
    session.delete(message)
    session.flush()
    return True


# ============================================================================
# KnowledgeChunk Repository Functions
# ============================================================================

def upsert_knowledge_chunk(
    session: Session,
    source: str,
    content: str,
    external_id: Optional[str] = None,
    title: Optional[str] = None,
    chunk_metadata: Optional[Dict[str, Any]] = None
) -> KnowledgeChunk:
    """
    Insert or update a knowledge chunk.
    
    If external_id is provided and a chunk with that external_id exists,
    it will be updated. Otherwise, a new chunk is created.
    
    Args:
        session: Database session
        source: Source of the chunk (e.g., "enhanced_readme")
        content: Chunk content
        external_id: External identifier (used for upsert logic)
        title: Chunk title (optional)
        chunk_metadata: Additional metadata (optional)
    
    Returns:
        Created or updated KnowledgeChunk object
    """
    if external_id:
        # Try to find existing chunk
        existing = session.query(KnowledgeChunk).filter(
            KnowledgeChunk.external_id == external_id,
            KnowledgeChunk.source == source
        ).first()
        
        if existing:
            # Update existing chunk
            existing.content = content
            if title is not None:
                existing.title = title
            if chunk_metadata is not None:
                existing.chunk_metadata = chunk_metadata
            session.flush()
            return existing
    
    # Create new chunk
    chunk = KnowledgeChunk(
        source=source,
        external_id=external_id,
        title=title,
        content=content,
        chunk_metadata=chunk_metadata
    )
    session.add(chunk)
    session.flush()
    return chunk


def get_knowledge_chunk_by_id(session: Session, chunk_id: UUID) -> Optional[KnowledgeChunk]:
    """
    Get knowledge chunk by ID.
    
    Args:
        session: Database session
        chunk_id: KnowledgeChunk UUID
    
    Returns:
        KnowledgeChunk object or None if not found
    """
    return session.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()


def get_knowledge_chunk_by_external_id(
    session: Session,
    external_id: str,
    source: Optional[str] = None
) -> Optional[KnowledgeChunk]:
    """
    Get knowledge chunk by external ID.
    
    Args:
        session: Database session
        external_id: External identifier
        source: Optional source filter
    
    Returns:
        KnowledgeChunk object or None if not found
    """
    query = session.query(KnowledgeChunk).filter(KnowledgeChunk.external_id == external_id)
    
    if source:
        query = query.filter(KnowledgeChunk.source == source)
    
    return query.first()


def search_knowledge_chunks_by_source(
    session: Session,
    source: str,
    limit: int = 100,
    offset: int = 0
) -> List[KnowledgeChunk]:
    """
    Search knowledge chunks by source.
    
    Args:
        session: Database session
        source: Source to filter by
        limit: Maximum number of chunks to return
        offset: Number of chunks to skip
    
    Returns:
        List of KnowledgeChunk objects
    """
    return session.query(KnowledgeChunk).filter(
        KnowledgeChunk.source == source
    ).order_by(KnowledgeChunk.created_at).offset(offset).limit(limit).all()


def list_all_knowledge_chunks(
    session: Session,
    limit: int = 100,
    offset: int = 0
) -> List[KnowledgeChunk]:
    """
    List all knowledge chunks with pagination.
    
    Args:
        session: Database session
        limit: Maximum number of chunks to return
        offset: Number of chunks to skip
    
    Returns:
        List of KnowledgeChunk objects
    """
    return session.query(KnowledgeChunk).order_by(
        KnowledgeChunk.created_at
    ).offset(offset).limit(limit).all()


def delete_knowledge_chunk(session: Session, chunk_id: UUID) -> bool:
    """
    Delete a knowledge chunk.
    
    Args:
        session: Database session
        chunk_id: KnowledgeChunk UUID
    
    Returns:
        True if chunk was deleted, False if not found
    """
    chunk = get_knowledge_chunk_by_id(session, chunk_id)
    if not chunk:
        return False
    
    session.delete(chunk)
    session.flush()
    return True


def bulk_upsert_knowledge_chunks(
    session: Session,
    chunks: List[Dict[str, Any]]
) -> List[KnowledgeChunk]:
    """
    Bulk upsert knowledge chunks.
    
    Args:
        session: Database session
        chunks: List of chunk dictionaries with keys:
            - source (required)
            - content (required)
            - external_id (optional, used for upsert)
            - title (optional)
            - chunk_metadata (optional)
    
    Returns:
        List of created/updated KnowledgeChunk objects
    """
    results = []
    for chunk_data in chunks:
        chunk = upsert_knowledge_chunk(
            session,
            source=chunk_data["source"],
            content=chunk_data["content"],
            external_id=chunk_data.get("external_id"),
            title=chunk_data.get("title"),
            chunk_metadata=chunk_data.get("chunk_metadata")
        )
        results.append(chunk)
    
    return results

