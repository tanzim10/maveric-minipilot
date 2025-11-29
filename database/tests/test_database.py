"""
End-to-end test script for database layer.

This script verifies all CRUD operations, relationships, and edge cases
for User, Conversation, Message, and KnowledgeChunk models.
"""

import sys
import time
from pathlib import Path
from uuid import UUID
from typing import Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from database.db_config import get_session, reset_db, get_engine
from database.models import User, Conversation, Message, KnowledgeChunk, MessageSenderType
from database.repository import (
    # User functions
    create_user, get_user_by_id, get_user_by_email, get_user_by_external_id,
    get_or_create_user_by_external_id, list_users, update_user, delete_user,
    # Conversation functions
    create_conversation, get_conversation_by_id, list_conversations_for_user,
    list_all_conversations, update_conversation, archive_conversation, delete_conversation,
    # Message functions
    add_message, get_message_by_id, list_messages_for_conversation,
    get_conversation_message_count, delete_message,
    # KnowledgeChunk functions
    upsert_knowledge_chunk, get_knowledge_chunk_by_id, get_knowledge_chunk_by_external_id,
    search_knowledge_chunks_by_source, list_all_knowledge_chunks, delete_knowledge_chunk,
    bulk_upsert_knowledge_chunks
)


def reset_database():
    """Reset database for clean test run."""
    print("\n" + "="*60)
    print("RESETTING DATABASE")
    print("="*60)
    reset_db()
    print("✓ Database reset complete\n")


def test_user_operations() -> Tuple[UUID, UUID]:
    """Test all user CRUD operations."""
    print("\n" + "="*60)
    print("TEST 1: User Operations")
    print("="*60)
    
    with get_session() as session:
        timestamp = int(time.time() * 1000)
        test_email = f"test_user_{timestamp}@example.com"
        test_external_id = f"auth_{timestamp}"
        
        print("\n1.1 Creating user...")
        user = create_user(
            session,
            email=test_email,
            name="Test User",
            external_id=test_external_id
        )
        assert user.id is not None
        assert user.email == test_email
        print(f"   ✓ User created: {user.id}")
        
        print("\n1.2 Retrieving user by ID...")
        retrieved_user = get_user_by_id(session, user.id)
        assert retrieved_user is not None
        assert retrieved_user.email == test_email
        print(f"   ✓ User retrieved: {retrieved_user.id}")
        
        print("\n1.3 Retrieving user by email...")
        user_by_email = get_user_by_email(session, test_email)
        assert user_by_email is not None
        assert user_by_email.id == user.id
        print(f"   ✓ User found by email")
        
        print("\n1.4 Retrieving user by external_id...")
        user_by_external = get_user_by_external_id(session, test_external_id)
        assert user_by_external is not None
        assert user_by_external.id == user.id
        print(f"   ✓ User found by external_id")
        
        print("\n1.5 Get or create user (existing)...")
        user2, created = get_or_create_user_by_external_id(
            session, test_external_id, email="different@example.com"
        )
        assert not created
        assert user2.id == user.id
        print(f"   ✓ Existing user returned (not created)")
        
        print("\n1.6 Get or create user (new)...")
        new_external_id = f"auth_new_{timestamp}"
        new_user, created = get_or_create_user_by_external_id(
            session, new_external_id, email=f"new_{timestamp}@example.com", name="New User"
        )
        assert created
        assert new_user.id is not None
        print(f"   ✓ New user created: {new_user.id}")
        
        print("\n1.7 Listing users...")
        all_users = list_users(session, limit=10)
        assert len(all_users) >= 2
        print(f"   ✓ Found {len(all_users)} users")
        
        print("\n1.8 Updating user...")
        updated_user = update_user(session, user.id, name="Updated Name")
        assert updated_user is not None
        assert updated_user.name == "Updated Name"
        print(f"   ✓ User updated: {updated_user.name}")
        
        return user.id, new_user.id


def test_conversation_operations(user_id: UUID) -> UUID:
    """Test all conversation CRUD operations."""
    print("\n" + "="*60)
    print("TEST 2: Conversation Operations")
    print("="*60)
    
    with get_session() as session:
        print("\n2.1 Creating conversation with user...")
        conversation = create_conversation(
            session,
            user_id=user_id,
            title="Test Conversation"
        )
        assert conversation.id is not None
        assert conversation.user_id == user_id
        assert conversation.status == "active"
        print(f"   ✓ Conversation created: {conversation.id}")
        
        print("\n2.2 Creating anonymous conversation...")
        anonymous_conv = create_conversation(session, title="Anonymous Chat")
        assert anonymous_conv.id is not None
        assert anonymous_conv.user_id is None
        print(f"   ✓ Anonymous conversation created: {anonymous_conv.id}")
        
        print("\n2.3 Retrieving conversation by ID...")
        retrieved_conv = get_conversation_by_id(session, conversation.id)
        assert retrieved_conv is not None
        assert retrieved_conv.title == "Test Conversation"
        print(f"   ✓ Conversation retrieved")
        
        print("\n2.4 Listing conversations for user...")
        user_conversations = list_conversations_for_user(session, user_id)
        assert len(user_conversations) >= 1
        print(f"   ✓ Found {len(user_conversations)} conversations for user")
        
        print("\n2.5 Listing all conversations...")
        all_conversations = list_all_conversations(session)
        assert len(all_conversations) >= 2
        print(f"   ✓ Found {len(all_conversations)} total conversations")
        
        print("\n2.6 Updating conversation...")
        updated_conv = update_conversation(session, conversation.id, title="Updated Title")
        assert updated_conv is not None
        assert updated_conv.title == "Updated Title"
        print(f"   ✓ Conversation updated")
        
        print("\n2.7 Archiving conversation...")
        archived_conv = archive_conversation(session, conversation.id)
        assert archived_conv is not None
        assert archived_conv.status == "archived"
        print(f"   ✓ Conversation archived")
        
        print("\n2.8 Listing archived conversations...")
        archived_convs = list_conversations_for_user(session, user_id, status="archived")
        assert len(archived_convs) >= 1
        print(f"   ✓ Found {len(archived_convs)} archived conversations")
        
        return conversation.id


def test_message_operations(conversation_id: UUID) -> Tuple[UUID, UUID]:
    """Test all message CRUD operations."""
    print("\n" + "="*60)
    print("TEST 3: Message Operations")
    print("="*60)
    
    with get_session() as session:
        print("\n3.1 Adding user message...")
        user_msg = add_message(
            session,
            conversation_id=conversation_id,
            sender_type=MessageSenderType.USER,
            content="Hello, how does the database work?",
            role_metadata={"tokens": 10}
        )
        assert user_msg.id is not None
        assert user_msg.sender_type == MessageSenderType.USER
        print(f"   ✓ User message added: {user_msg.id}")
        
        print("\n3.2 Adding assistant message...")
        assistant_msg = add_message(
            session,
            conversation_id=conversation_id,
            sender_type=MessageSenderType.ASSISTANT,
            content="The database uses SQLAlchemy with PostgreSQL/SQLite support.",
            role_metadata={
                "tokens": 15,
                "model": "gpt-4",
                "retrieved_chunks": ["chunk1", "chunk2"]
            }
        )
        assert assistant_msg.id is not None
        assert assistant_msg.sender_type == MessageSenderType.ASSISTANT
        print(f"   ✓ Assistant message added: {assistant_msg.id}")
        
        print("\n3.3 Adding system message...")
        system_msg = add_message(
            session,
            conversation_id=conversation_id,
            sender_type=MessageSenderType.SYSTEM,
            content="Error: Connection timeout"
        )
        assert system_msg.id is not None
        print(f"   ✓ System message added: {system_msg.id}")
        
        print("\n3.4 Retrieving message by ID...")
        retrieved_msg = get_message_by_id(session, user_msg.id)
        assert retrieved_msg is not None
        assert retrieved_msg.content == "Hello, how does the database work?"
        print(f"   ✓ Message retrieved")
        
        print("\n3.5 Listing messages for conversation...")
        messages = list_messages_for_conversation(session, conversation_id)
        assert len(messages) >= 3
        print(f"   ✓ Found {len(messages)} messages in conversation")
        
        print("\n3.6 Filtering messages by sender type...")
        user_messages = list_messages_for_conversation(
            session, conversation_id, sender_type=MessageSenderType.USER
        )
        assert len(user_messages) >= 1
        print(f"   ✓ Found {len(user_messages)} user messages")
        
        print("\n3.7 Getting message count...")
        count = get_conversation_message_count(session, conversation_id)
        assert count >= 3
        print(f"   ✓ Conversation has {count} messages")
        
        return user_msg.id, assistant_msg.id


def test_knowledge_chunk_operations() -> UUID:
    """Test all knowledge chunk CRUD operations."""
    print("\n" + "="*60)
    print("TEST 4: KnowledgeChunk Operations")
    print("="*60)
    
    with get_session() as session:
        print("\n4.1 Creating knowledge chunk...")
        chunk = upsert_knowledge_chunk(
            session,
            source="enhanced_readme",
            external_id="readme_section_1",
            title="Installation Guide",
            content="To install the project, run: pip install -r requirements.txt",
            chunk_metadata={"section_type": "installation", "module": "readme_generator"}
        )
        assert chunk.id is not None
        assert chunk.source == "enhanced_readme"
        print(f"   ✓ Knowledge chunk created: {chunk.id}")
        
        print("\n4.2 Upserting existing chunk (update)...")
        updated_chunk = upsert_knowledge_chunk(
            session,
            source="enhanced_readme",
            external_id="readme_section_1",
            content="To install the project, run: pip install -r requirements.txt\n\nFor development, use: pip install -e .",
            title="Installation Guide (Updated)"
        )
        assert updated_chunk.id == chunk.id
        assert "For development" in updated_chunk.content
        print(f"   ✓ Knowledge chunk updated (upsert)")
        
        print("\n4.3 Retrieving chunk by ID...")
        retrieved_chunk = get_knowledge_chunk_by_id(session, chunk.id)
        assert retrieved_chunk is not None
        assert retrieved_chunk.title == "Installation Guide (Updated)"
        print(f"   ✓ Chunk retrieved by ID")
        
        print("\n4.4 Retrieving chunk by external_id...")
        chunk_by_ext = get_knowledge_chunk_by_external_id(
            session, "readme_section_1", source="enhanced_readme"
        )
        assert chunk_by_ext is not None
        assert chunk_by_ext.id == chunk.id
        print(f"   ✓ Chunk retrieved by external_id")
        
        print("\n4.5 Searching chunks by source...")
        chunks = search_knowledge_chunks_by_source(session, "enhanced_readme")
        assert len(chunks) >= 1
        print(f"   ✓ Found {len(chunks)} chunks from enhanced_readme")
        
        print("\n4.6 Bulk upserting chunks...")
        bulk_chunks = [
            {
                "source": "docs",
                "external_id": "doc_section_1",
                "title": "API Reference",
                "content": "The API provides endpoints for...",
                "chunk_metadata": {"section": "api"}
            },
            {
                "source": "docs",
                "external_id": "doc_section_2",
                "title": "Configuration",
                "content": "Configuration is done via...",
                "chunk_metadata": {"section": "config"}
            }
        ]
        bulk_results = bulk_upsert_knowledge_chunks(session, bulk_chunks)
        assert len(bulk_results) == 2
        print(f"   ✓ Bulk upserted {len(bulk_results)} chunks")
        
        print("\n4.7 Listing all chunks...")
        all_chunks = list_all_knowledge_chunks(session, limit=10)
        assert len(all_chunks) >= 3
        print(f"   ✓ Found {len(all_chunks)} total chunks")
        
        return chunk.id


def test_relationships(user_id: UUID, conversation_id: UUID):
    """Test model relationships and cascade deletes."""
    print("\n" + "="*60)
    print("TEST 5: Relationships & Cascade Deletes")
    print("="*60)
    
    with get_session() as session:
        print("\n5.1 Testing User -> Conversation relationship...")
        user = get_user_by_id(session, user_id)
        assert user is not None
        conv_count = user.conversations.count()
        assert conv_count >= 1
        print(f"   ✓ User has {conv_count} conversations")
        
        print("\n5.2 Testing Conversation -> Message relationship...")
        conversation = get_conversation_by_id(session, conversation_id)
        assert conversation is not None
        msg_count = conversation.messages.count()
        assert msg_count >= 1
        print(f"   ✓ Conversation has {msg_count} messages")
        
        print("\n5.3 Testing cascade delete (Conversation -> Messages)...")
        # Create a new conversation with messages
        test_conv = create_conversation(session, user_id=user_id, title="Test Cascade")
        test_msg = add_message(
            session, test_conv.id, MessageSenderType.USER, "Test message"
        )
        test_conv_id = test_conv.id
        test_msg_id = test_msg.id
        
        # Delete conversation
        delete_conversation(session, test_conv_id)
        
        # Verify message was also deleted
        deleted_msg = get_message_by_id(session, test_msg_id)
        assert deleted_msg is None
        print(f"   ✓ Messages deleted when conversation deleted (cascade)")
        
        print("\n5.4 Testing cascade delete (User -> Conversations)...")
        # Create a new user with conversation
        test_user = create_user(session, email=f"cascade_test_{int(time.time())}@example.com")
        test_user_conv = create_conversation(session, user_id=test_user.id, title="Test")
        test_user_conv_id = test_user_conv.id
        
        # Delete user
        delete_user(session, test_user.id)
        
        # Verify conversation was also deleted
        deleted_conv = get_conversation_by_id(session, test_user_conv_id)
        assert deleted_conv is None
        print(f"   ✓ Conversations deleted when user deleted (cascade)")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "="*60)
    print("TEST 6: Edge Cases")
    print("="*60)
    
    with get_session() as session:
        print("\n6.1 Getting non-existent user...")
        fake_id = UUID("00000000-0000-0000-0000-000000000000")
        user = get_user_by_id(session, fake_id)
        assert user is None
        print(f"   ✓ Non-existent user returns None")
        
        print("\n6.2 Updating non-existent conversation...")
        updated = update_conversation(session, fake_id, title="Test")
        assert updated is None
        print(f"   ✓ Updating non-existent conversation returns None")
        
        print("\n6.3 Listing with pagination (empty result)...")
        users = list_users(session, limit=10, offset=10000)
        assert len(users) == 0
        print(f"   ✓ Empty pagination handled correctly")
        
        print("\n6.4 Creating user without email or external_id...")
        anonymous_user = create_user(session, name="Anonymous")
        assert anonymous_user.id is not None
        assert anonymous_user.email is None
        print(f"   ✓ Anonymous user created successfully")


def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*60)
    print("DATABASE LAYER END-TO-END TESTS")
    print("="*60)
    
    # Reset database for clean test run
    reset_database()
    
    try:
        # Run test suites
        user_id, new_user_id = test_user_operations()
        conversation_id = test_conversation_operations(user_id)
        user_msg_id, assistant_msg_id = test_message_operations(conversation_id)
        chunk_id = test_knowledge_chunk_operations()
        test_relationships(user_id, conversation_id)
        test_edge_cases()
        
        # Summary
        print("\n" + "="*60)
        print("ALL TESTS PASSED")
        print("="*60)
        print("\nTest Summary:")
        print(f"  ✓ User operations: PASSED")
        print(f"  ✓ Conversation operations: PASSED")
        print(f"  ✓ Message operations: PASSED")
        print(f"  ✓ KnowledgeChunk operations: PASSED")
        print(f"  ✓ Relationships & cascades: PASSED")
        print(f"  ✓ Edge cases: PASSED")
        print("\nDatabase layer is working correctly!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_all_tests()

